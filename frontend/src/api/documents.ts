import client from './client';
import type { Document, DocumentDetail } from '../types';

export const getDocuments = async (params?: { project_id?: number; status?: string; search?: string }): Promise<Document[]> => {
  const { data } = await client.get('/api/documents/', { params });
  return data;
};

export const getDocument = async (id: number): Promise<DocumentDetail> => {
  const { data } = await client.get(`/api/documents/${id}`);
  return data;
};
