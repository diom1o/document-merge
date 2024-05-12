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
    const contentState = editorState.getCurrentContent();
    documentSocket.emit('save-document', JSON.stringify(convertToRaw(contentState)));
  },
  onEdit: (editorState: EditorState) => {
    const contentState = editorState.getCurrentContent();
    documentSocket.emit('edit-document', JSON.stringify(convertToRaw(contentState)));
  }
});

const editorPlugins = [documentEditSocketPlugin];

const DocumentEditor: React.FC = () => {
  const editorRef = useRef<Editor>(null);
  const [currentEditorState, setCurrentEditorState] = useState(() => EditorState.createEmpty());

  useEffect(() => {
    documentSocket.emit('load-document');
    documentSocket.on('document', (documentContent: string) => {
      const contentFromRaw = convertFromRaw(JSON.parse(documentContent));
      setCurrentEditorState(EditorState.createWithContent(contentFromRaw));
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