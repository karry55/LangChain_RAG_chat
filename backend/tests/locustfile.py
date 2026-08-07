"""
Locust 压力测试 — RAG 知识库问答系统

测试场景：
  - 轻量级：登录 + 查询会话列表
  - 中等：用户注册
  - 重量级：RAG 流式问答
  - 混合：80% 查询 + 15% 问答 + 5% 注册

启动方式：
  cd backend
  locust -f tests/locustfile.py
  浏览器打开 http://localhost:8089

运行前准备：
  python tests/setup_test_users.py
"""
import random
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner


# --- 测试配置 ---
TEST_USER_PREFIX = "testuser"
TEST_USER_COUNT = 100
TEST_PASSWORD = "test123456"

# RAG 问答的测试问题池
TEST_QUESTIONS = [
    "华为Mate 60 Pro的电池容量是多少？",
    "iPhone 15 Pro Max支持快充吗？",
    "AirPods Pro 2的价格是多少？",
    "MacBook Pro 14的屏幕尺寸？",
    "索尼WH-1000XM5的续航时间？",
    "ThinkPad X1 Carbon的重量？",
    "Mate 60 Pro支持卫星通话吗？",
    "iPhone 15的摄像头像素？",
    "MacBook的电池续航多久？",
    "AirPods防水等级？",
]


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Locust 启动时调用，检查环境"""
    if isinstance(environment.runner, MasterRunner):
        print("\n[Locust] Locust Web UI: http://localhost:8089\n")


class WebsiteUser(HttpUser):
    """模拟用户行为"""
    wait_time = between(1, 3)  # 操作间隔 1-3 秒
    host = "http://localhost:8000"

    def on_start(self):
        """每个虚拟用户启动时执行：登录获取 Token"""
        # 随机选一个测试用户
        idx = random.randint(1, TEST_USER_COUNT)
        username = f"{TEST_USER_PREFIX}{idx:03d}"

        resp = self.client.post("/api/auth/login", json={
            "username": username,
            "password": TEST_PASSWORD,
        })
        if resp.status_code == 200:
            data = resp.json()
            self.token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            # 可能是测试用户还没创建，尝试注册
            resp = self.client.post("/api/auth/register", json={
                "username": username,
                "password": TEST_PASSWORD,
            })
            if resp.status_code in (200, 201):
                data = resp.json()
                self.token = data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
            else:
                self.token = None
                self.headers = {}

    # --- 场景 1：轻量级 ---
    @task(5)
    def list_conversations(self):
        """查询会话列表（轻量读操作）"""
        if not self.token:
            return
        with self.client.get(
            "/api/conversations",
            headers=self.headers,
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    # --- 场景 2：轻量级 ---
    @task(3)
    def get_my_info(self):
        """获取当前用户信息"""
        if not self.token:
            return
        with self.client.get(
            "/api/auth/me",
            headers=self.headers,
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    # --- 场景 3：重量级 ---
    @task(1)
    def chat_query(self):
        """RAG 流式问答（核心重操作）"""
        if not self.token:
            return
        question = random.choice(TEST_QUESTIONS)

        with self.client.post(
            "/api/chat/query",
            json={"message": question},
            headers={**self.headers, "Content-Type": "application/json"},
            catch_response=True,
            stream=True,
            timeout=30,
        ) as resp:
            if resp.status_code == 200:
                # 消费 SSE 流（不计入延迟，但验证连接稳定性）
                chunk_count = 0
                try:
                    for line in resp.iter_lines(decode_unicode=True):
                        if line and line.startswith("data:"):
                            chunk_count += 1
                except Exception:
                    pass
                if chunk_count > 0:
                    resp.success()
                else:
                    resp.failure("SSE stream returned no data")
            else:
                resp.failure(f"Status: {resp.status_code}")


class RegistrationUser(HttpUser):
    """模拟新用户注册场景（测试 SQLite 写锁）"""
    wait_time = between(2, 5)
    host = "http://localhost:8000"

    @task
    def register(self):
        """注册新用户"""
        # 用时间戳+随机数确保用户名唯一
        import time
        username = f"stress_{int(time.time() * 1000) % 100000}_{random.randint(0, 999)}"

        with self.client.post(
            "/api/auth/register",
            json={
                "username": username,
                "password": "stress123",
                "email": f"{username}@stress.test",
            },
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 201):
                resp.success()
            elif resp.status_code == 409:
                resp.success()  # 用户名重复也算通过（测试环境正常）
            else:
                resp.failure(f"Status: {resp.status_code}")


class AdminUser(HttpUser):
    """模拟管理员操作（知识库查询）"""
    wait_time = between(3, 6)
    host = "http://localhost:8000"

    def on_start(self):
        resp = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "123456",
        })
        if resp.status_code == 200:
            self.token = resp.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @task(3)
    def get_documents(self):
        """查询知识库文档列表"""
        if not self.token:
            return
        with self.client.get(
            "/api/knowledge/documents",
            headers=self.headers,
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    @task(1)
    def get_knowledge_stats(self):
        """查询知识库统计"""
        if not self.token:
            return
        with self.client.get(
            "/api/knowledge/stats",
            headers=self.headers,
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")
