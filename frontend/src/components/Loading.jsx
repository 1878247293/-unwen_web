import React from 'react'
import { Spin } from 'antd'
import { LoadingOutlined } from '@ant-design/icons'
import './Loading.css'

const Loading = ({
  size = 'default',
  fullScreen = false,
  tip = '加载中...',
  type = 'spinner' // spinner, dots, pulse
}) => {
  const customIcon = <LoadingOutlined style={{ fontSize: size === 'large' ? 48 : size === 'small' ? 24 : 36 }} spin />

  if (type === 'dots') {
    return (
      <div className={`loading-container ${fullScreen ? 'fullscreen' : ''}`}>
        <div className="loading-dots">
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
        </div>
        {tip && <p className="loading-tip">{tip}</p>}
      </div>
    )
  }

  if (type === 'pulse') {
    return (
      <div className={`loading-container ${fullScreen ? 'fullscreen' : ''}`}>
        <div className="loading-pulse">
          <div className="pulse-circle"></div>
          <div className="pulse-circle delay-1"></div>
          <div className="pulse-circle delay-2"></div>
        </div>
        {tip && <p className="loading-tip">{tip}</p>}
      </div>
    )
  }

  // Default spinner
  return (
    <div className={`loading-container ${fullScreen ? 'fullscreen' : ''}`}>
      <Spin indicator={customIcon} tip={tip} size={size} />
    </div>
  )
}

export default Loading
