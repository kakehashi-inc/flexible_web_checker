// このファイルはプロジェクトの型定義ディレクトリ (例: frontend/ts/@types/styled-jsx.d.ts) に配置します。
import 'react';

declare module 'react' {
  interface StyleHTMLAttributes<T> extends React.HTMLAttributes<T> {
    jsx?: boolean;
    global?: boolean;
  }
}
