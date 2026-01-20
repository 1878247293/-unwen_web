import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import 'dayjs/locale/zh-cn'
import App from './App.jsx'
import './assets/styles/index.css'
import './assets/styles/modern-academic-theme.css'
import './assets/styles/print.css'

// 为 react-markdown-editor-lite 提供全局 React 和 ReactDOM
window.React = React
window.ReactDOM = ReactDOM

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ConfigProvider locale={zhCN}>
        <App />
      </ConfigProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
