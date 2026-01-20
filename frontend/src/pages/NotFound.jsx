import React from 'react'
import { Button, Result } from 'antd'
import { useNavigate } from 'react-router-dom'
import { HomeOutlined, ArrowLeftOutlined } from '@ant-design/icons'
import './NotFound.css'

const NotFound = () => {
  const navigate = useNavigate()

  return (
    <div className="not-found-container">
      {/* 背景装饰 */}
      <div className="background-shapes">
        <div className="shape-404"></div>
        <div className="shape-404 delay-1"></div>
        <div className="shape-404 delay-2"></div>
      </div>

      <div className="not-found-content">
        {/* 404动画数字 */}
        <div className="error-code">
          <span className="digit">4</span>
          <span className="digit middle">0</span>
          <span className="digit">4</span>
        </div>

        <h1 className="error-title">页面未找到</h1>
        <p className="error-description">
          抱歉，您访问的页面不存在或已被移除
        </p>

        <div className="error-actions">
          <Button
            type="primary"
            size="large"
            icon={<HomeOutlined />}
            onClick={() => navigate('/')}
            className="error-button"
          >
            返回首页
          </Button>
          <Button
            size="large"
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(-1)}
            className="error-button secondary"
          >
            返回上一页
          </Button>
        </div>

        {/* 浮动图标 */}
        <div className="floating-icons">
          <div className="floating-icon icon-1">📄</div>
          <div className="floating-icon icon-2">📚</div>
          <div className="floating-icon icon-3">🔍</div>
          <div className="floating-icon icon-4">💡</div>
        </div>
      </div>
    </div>
  )
}

export default NotFound
