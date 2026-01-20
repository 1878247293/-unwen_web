/**
 * 背景装饰组件 - 现代学术风格
 * 包含右上角的几何网格和左下角的书籍轮廓
 */
import React from 'react'
import './BackgroundDecoration.css'

const BackgroundDecoration = () => {
  return (
    <div className="background-decoration">
      {/* 右上角几何网格 */}
      <svg
        className="decoration-grid"
        viewBox="0 0 400 400"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* 六边形网格 */}
        <g opacity="0.15" stroke="#1890ff" strokeWidth="1.5">
          {/* 第一排 */}
          <polygon points="50,50 70,40 90,50 90,70 70,80 50,70" />
          <polygon points="90,50 110,40 130,50 130,70 110,80 90,70" />
          <polygon points="130,50 150,40 170,50 170,70 150,80 130,70" />
          <polygon points="170,50 190,40 210,50 210,70 190,80 170,70" />

          {/* 第二排 */}
          <polygon points="70,90 90,80 110,90 110,110 90,120 70,110" />
          <polygon points="110,90 130,80 150,90 150,110 130,120 110,110" />
          <polygon points="150,90 170,80 190,90 190,110 170,120 150,110" />
          <polygon points="190,90 210,80 230,90 230,110 210,120 190,110" />

          {/* 第三排 */}
          <polygon points="90,130 110,120 130,130 130,150 110,160 90,150" />
          <polygon points="130,130 150,120 170,130 170,150 150,160 130,150" />
          <polygon points="170,130 190,120 210,130 210,150 190,160 170,150" />
        </g>

        {/* 连接线 */}
        <g opacity="0.08" stroke="#52c41a" strokeWidth="1">
          <line x1="70" y1="40" x2="150" y2="120" />
          <line x1="150" y1="40" x2="90" y2="120" />
          <line x1="110" y1="40" x2="190" y2="120" />
        </g>

        {/* 圆点装饰 */}
        <g opacity="0.2" fill="#faad14">
          <circle cx="70" cy="40" r="3" />
          <circle cx="150" cy="40" r="3" />
          <circle cx="130" cy="80" r="3" />
          <circle cx="90" cy="120" r="3" />
          <circle cx="170" cy="120" r="3" />
        </g>
      </svg>

      {/* 左下角书籍轮廓 */}
      <svg
        className="decoration-books"
        viewBox="0 0 300 300"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* 书籍堆叠 */}
        <g opacity="0.1" stroke="#1f2937" strokeWidth="2">
          {/* 第一本书 */}
          <rect x="50" y="180" width="100" height="15" rx="2" fill="#e8ecf1" />
          <line x1="70" y1="180" x2="70" y2="195" stroke="#d1d5db" strokeWidth="1" />
          <line x1="90" y1="180" x2="90" y2="195" stroke="#d1d5db" strokeWidth="1" />

          {/* 第二本书 */}
          <rect x="60" y="160" width="90" height="15" rx="2" fill="#e8ecf1" />
          <line x1="80" y1="160" x2="80" y2="175" stroke="#d1d5db" strokeWidth="1" />
          <line x1="100" y1="160" x2="100" y2="175" stroke="#d1d5db" strokeWidth="1" />

          {/* 第三本书 */}
          <rect x="55" y="140" width="95" height="15" rx="2" fill="#e8ecf1" />
          <line x1="75" y1="140" x2="75" y2="155" stroke="#d1d5db" strokeWidth="1" />
          <line x1="95" y1="140" x2="95" y2="155" stroke="#d1d5db" strokeWidth="1" />

          {/* 第四本书 */}
          <rect x="65" y="120" width="85" height="15" rx="2" fill="#e8ecf1" />
          <line x1="85" y1="120" x2="85" y2="135" stroke="#d1d5db" strokeWidth="1" />
          <line x1="105" y1="120" x2="105" y2="135" stroke="#d1d5db" strokeWidth="1" />
        </g>

        {/* 文档图标 */}
        <g opacity="0.08" stroke="#1890ff" strokeWidth="2" fill="none">
          <rect x="170" y="150" width="60" height="80" rx="4" />
          <line x1="180" y1="165" x2="220" y2="165" />
          <line x1="180" y1="180" x2="220" y2="180" />
          <line x1="180" y1="195" x2="210" y2="195" />
        </g>
      </svg>
    </div>
  )
}

export default BackgroundDecoration
