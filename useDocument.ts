import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_BASE_URL;

interface Document {
  id?: string;
  content?: string;
}

interface UseDocumentManagerProps {
  onConflict?: () => void;
  onFetchError?: (error: any) => void;
  onSaveError?: (error: any) => void;
  onMergeError?: (error: any) => void;
}

export const useDocumentManager = ({
  onConflict,
  onFetchError,
  onSaveError,
  onMergeError,
}: UseDocumentManagerProps) => {
  const [document, setDocument] = useState<Document>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchDocument = async (id: string) => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/documents/${id}`);
      setDocument(response.data);
    } catch (error) {
      onFetchError?.(error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveDocument = async (doc: Document) => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/documents`, doc);
      setDocument(response.data);
    } catch (error) {
      onSaveError?.(error);
    } finally {
      setIsLoading(false);
    }
  };

  const mergeDocument = async (id: string, updates: Partial<Document>) => {
    setIsLoading(true);
    try {
      const response = await axios.patch(`${API_BASE_URL}/documents/${id}`, updates);
      setDocument(response.data);
    } catch (error) {
      if (error.response?.status === 409) {
        onConflict?.();
      } else {
        onMergeError?.(error);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
  }, []);

  return { document, isLoading, fetchDocument, saveDocument, mergeDocument };
};