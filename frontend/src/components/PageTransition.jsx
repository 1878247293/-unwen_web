import React from 'react'
import { useLocation, useOutlet } from 'react-router-dom'
import { CSSTransition, SwitchTransition } from 'react-transition-group'
import './PageTransition.css'

/**
 * 页面切换动画组件
 * 使用React Router v6 + react-transition-group实现平滑的页面切换效果
 */
const PageTransition = ({
  mode = 'fade',  // fade, slide-left, slide-right, slide-up, zoom
  timeout = 300,
  children
}) => {
  const location = useLocation()
  const currentOutlet = useOutlet()

  return (
    <SwitchTransition mode="out-in">
      <CSSTransition
        key={location.pathname}
        timeout={timeout}
        classNames={`page-transition-${mode}`}
        unmountOnExit
      >
        <div className="page-transition-wrapper">
          {children || currentOutlet}
        </div>
      </CSSTransition>
    </SwitchTransition>
  )
}

export default PageTransition
