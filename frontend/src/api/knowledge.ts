import client from './client';

export interface DocumentItem {
  id: string;
  title: string;
  description: string;
  file_type: string;
  file_size: number;
  status: string;
  chunk_count: number;
  error_message: string;
  uploaded_by: string;
  created_at: string;
  updated_at: string;
}

export interface ChunkItem {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  token_count: number;
  created_at: string;
}

export interface KnowledgeStats {
  total_documents: number;
  processed_documents: number;
  failed_documents: number;
  total_chunks: number;
  total_file_size: number;
}

export async function uploadDocument(file: File, description = '') {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('description', description);

  const res = await client.post('/knowledge/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function getDocuments(page = 1, pageSize = 20) {
  const res = await client.get('/knowledge/documents', {
    params: { page, page_size: pageSize },
  });
  return res.data;
}

export async function getDocumentChunks(docId: string, page = 1, pageSize = 50) {
  const res = await client.get(`/knowledge/documents/${docId}/chunks`, {
    params: { page, page_size: pageSize },
  });
  return res.data;
}

export async function deleteDocument(docId: string) {
  const res = await client.delete(`/knowledge/documents/${docId}`);
  return res.data;
}

export async function getKnowledgeStats() {
  const res = await client.get('/knowledge/stats');
  return res.data;
}
