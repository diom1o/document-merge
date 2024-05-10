import React, { useEffect, useRef, useState } from 'react';
import { EditorState, convertFromRaw, convertToRaw } from 'draft-js';
import 'draft-js/dist/Draft.css';
import Editor from "@draft-js-plugins/editor";
import createSocketIoPlugin from '@draft-js-plugins/socket-io';
import io from 'socket.io-client';

const SERVER_URL = process.env.REACT_APP_SERVER_URL || 'http://localhost:8080';
const SOCKET_PATH = process.env.REACT_APP_SOCKET_PATH || '/socket.io';

const socket = io(SERVER_URL, { path: SOCKET_PATH });

const socketIoPlugin = createSocketIoPlugin({
  socket: socket,
  onSave: (editorState: EditorState) => {
    const content = editorState.getCurrentContent();
    socket.emit('save-document', JSON.stringify(convertToRaw(content)));
  },
  onEdit: (editorState: EditorState) => {
    const content = editorState.getCurrentContent();
    socket.emit('edit-document', JSON.stringify(convertToRaw(content)));
  }
});

const plugins = [socketIoPlugin];

const DocumentEditor: React.FC = () => {
  const editor = useRef<Editor>(null);
  const [editorState, setEditorState] = useState(() => EditorState.createEmpty());

  useEffect(() => {
    socket.emit('load-document');
    socket.on('document', (doc: string) => {
      const contentState = convertFromRaw(JSON.parse(doc));
      setEditorState(EditorState.createWithContent(contentState));
    });

    return () => {
      socket.off('document');
    };
  }, []);

  useEffect(() => {
    if (editor.current) editor.current.focus();
  }, []);

  const onChange = (newEditorState: EditorState) => {
    setEditorState(newEditorState);
  };

  return (
    <div style={{ padding: '20px' }}>
      <Editor
        editorKey="document-editor"
        editorState={editorState}
        onChange={onChange}
        plugins={plugins}
        ref={editor}
      />
    </div>
  );
};

export default DocumentEditor;