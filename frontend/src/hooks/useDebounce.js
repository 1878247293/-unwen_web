import { useState, useEffect } from 'react'

/**
 * 防抖Hook
 * @param {*} value - 需要防抖的值
 * @param {number} delay - 延迟时间（毫秒），默认500ms
 * @returns {*} - 防抖后的值
 */
export const useDebounce = (value, delay = 500) => {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    // 设置定时器
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    // 清理函数：如果value在delay时间内再次改变，清除之前的定时器
    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

/**
 * 防抖回调Hook
 * @param {Function} callback - 需要防抖的回调函数
 * @param {number} delay - 延迟时间（毫秒），默认500ms
 * @returns {Function} - 防抖后的回调函数
 */
export const useDebouncedCallback = (callback, delay = 500) => {
  const [timer, setTimer] = useState(null)

  return (...args) => {
    if (timer) {
      clearTimeout(timer)
    }

    const newTimer = setTimeout(() => {
      callback(...args)
    }, delay)

    setTimer(newTimer)
  }
}

export default useDebounce
