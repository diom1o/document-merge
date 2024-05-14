import React, { useEffect, useRef, useState } from 'react';
import { EditorState, convertFromRaw, convertToRaw } from 'draft-js';
import 'draft-js/dist/Draft.css';
import Editor from "@draft-js-plugins/editor";
import createSocketIoPlugin from '@draft-js-plugins/socket-io';
import io from 'socket.io-client';

const SERVER_URL = process.env.REACT_APP_SERVER_URL || 'http://localhost:8080';
const SOCKET_PATH = process.env.REACT_APP_SOCKET_PATH || '/socket.io';

const documentSocket = io(SERVER_URL, { path: SOCKET_PATH });

const documentEditSocketPlugin = createSocketIoPlugin({
  socket: documentSocket,
  onSave: (editorState: EditorState) => {
    try {
      const contentState = editorState.getCurrentContent();
      documentSocket.emit('save-document', JSON.stringify(convertToRaw(contentState)));
    } catch (error) {
      console.error("Failed to save document:", error);
    }
  },
  onEdit: (editorState: EditorState) => {
    try {
      const contentState = editorState.getCurrentContent();
      documentSocket.emit('edit-document', JSON.stringify(convertToRaw(contentState)));
    } catch (error) {
      console.error("Failed to edit document:", error);
    }
  }
});

const editorPlugins = [documentEditSocketPlugin];

const DocumentEditor: React.FC = () => {
  const editorRef = useRef<Editor>(null);
  const [currentEditorState, setCurrentEditorState] = useState(() => EditorState.createEmpty());

  useEffect(() => {
    documentSocket.emit('load-document');
    documentSocket.on('document', (documentContent: string) => {
      try {
        const contentFromRaw = convertFromRaw(JSON.parse(documentContent));
        setCurrentEditorState(EditorState.createWithContent(contentFromRaw));
      } catch (error) {
        console.error("Error parsing document content:", error);
        // Optionally, set the editor to a default/empty state if the document could not be loaded correctly
        // setCurrentEditorState(EditorState.createEmpty());
      }
    });

    return () => {
      documentSocket.off('document');
    };
  }, []);

  useEffect(() => {
    if (editorRef.current) editorRef.current.focus();
  }, []);

  const handleEditorChange = (newEditorState: EditorState) => {
    setCurrentEditorState(newEditorState);
  };

  return (
    <div style={{ padding: '20px' }}>
      <Editor
        editorKey="document-editor"
        editorState={currentEditorState}
        onChange={handleEditorChange}
        plugins={editorPlugins}
        ref={editorRef}
      />
    </div>
  );
};

export default DocumentEditor;