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

type Cache<T> = { [key: string]: T };

export const useDocumentManager = ({
  onConflict,
  onFetchError,
  onSaveError,
  onMergeError,
}: UseDocumentManagerProps) => {
  const [document, setDocument] = useState<Document>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const documentCache: Cache<Document> = {}; // In-memory cache for documents

  const handleApiCall = async (apiCall: () => Promise<any>, onSuccess: (data: Document) => void) => {
    setIsLoading(true);
    try {
      const response = await apiCall();
      onSuccess(response.data);
    } catch (error) {
      if (error.response?.status === 409) {
        onConflict?.();
      } else {
        const errorHandler = error.config.method === 'get' ? onFetchError : error.config.method === 'post' ? onSaveError : onMergeError;
        errorHandler?.(error);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDocument = async (id: string) => {
    if (documentCache[id]) {
      setDocument(documentCache[id]);
      return;
    }
    
    await handleApiCall(
      () => axios.get<Document>(`${API_BASE_URL}/documents/${id}`),
      (data: Document) => {
        setDocument(data);
        documentCache[id] = data; // Cache the fetched document
      }
    );
  };

  const saveDocument = async (doc: Document) => {
    await handleApiCall(
      () => axios.post<Document>(`${API_BASE_URL}/documents`, doc),
      (data: Document) => {
        setDocument(data);
        // Cache the document using its id if available
        if (data.id) {
          documentCache[data.id] = data;
        }
      }
    );
  };

  const mergeDocument = async (id: string, updates: Partial<Document>) => {
    await handleApiCall(
      () => axios.patch<Document>(`${API_BASE_URL}/documents/${id}`, updates),
      (data: Document) => {
        setDocument(data);
        documentCache[id] = data; // Update the cache after a successful merge
      }
    );
  };

  // Note: The useEffect is removed since it's not being used.
  
  return { document, isLoading, fetchDocument, saveDocument, mergeDocument };
};