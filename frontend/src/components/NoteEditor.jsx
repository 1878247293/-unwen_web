/**
 * 笔记编辑器组件
 * 支持Markdown编辑、预览、自动保存
 */
import React, { useState, useEffect, useRef } from 'react'
import { Card, Button, Input, Select, message, Space, Modal } from 'antd'
import { SaveOutlined, EyeOutlined, EditOutlined } from '@ant-design/icons'
import MdEditor from 'react-markdown-editor-lite'
import MarkdownIt from 'markdown-it'
import 'react-markdown-editor-lite/lib/index.css'
import noteService from '../services/noteService'

const { Option } = Select

// 初始化Markdown解析器
const mdParser = new MarkdownIt()

// 笔记类型选项
const NOTE_TYPES = [
  { value: 'general', label: '一般笔记' },
  { value: 'summary', label: '总结' },
  { value: 'method', label: '方法' },
  { value: 'conclusion', label: '结论' },
  { value: 'innovation', label: '创新点' },
  { value: 'limitation', label: '局限性' },
  { value: 'thinking', label: '个人思考' }
]

// 笔记模板
const NOTE_TEMPLATES = {
  summary: `# 论文总结

## 研究背景
-

## 主要贡献
-

## 核心方法
-

## 实验结果
-

## 个人评价
-
`,
  method: `# 方法笔记

## 核心算法
-

## 技术细节
-

## 实现要点
-

## 可借鉴之处
-
`,
  innovation: `# 创新点分析

## 主要创新
-

## 与前人工作对比
-

## 创新的意义
-
`,
  limitation: `# 局限性分析

## 方法局限
-

## 实验局限
-

## 适用场景
-

## 改进方向
-
`,
  thinking: `# 个人思考

## 启发与想法
-

## 可能的应用
-

## 存在的问题
-

## 进一步探索
-
`
}

function NoteEditor({ paperId, note, onSave, onCancel }) {
  const [title, setTitle] = useState(note?.title || '')
  const [content, setContent] = useState(note?.content || '')
  const [noteType, setNoteType] = useState(note?.note_type || 'general')
  const [saving, setSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)
  const autoSaveTimerRef = useRef(null)

  // 应用模板
  const applyTemplate = () => {
    if (content && content.trim()) {
      Modal.confirm({
        title: '确认应用模板？',
        content: '当前内容将被替换，是否继续？',
        onOk: () => {
          const template = NOTE_TEMPLATES[noteType] || ''
          setContent(template)
          setHasChanges(true)
        }
      })
    } else {
      const template = NOTE_TEMPLATES[noteType] || ''
      setContent(template)
      setHasChanges(true)
    }
  }

  // 内容变化处理
  const handleEditorChange = ({ text }) => {
    setContent(text)
    setHasChanges(true)

    // 重置自动保存计时器
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current)
    }

    // 30秒后自动保存
    autoSaveTimerRef.current = setTimeout(() => {
      if (note?.id) {
        handleAutoSave()
      }
    }, 30000) // 30秒
  }

  // 自动保存
  const handleAutoSave = async () => {
    if (!hasChanges || !note?.id) return

    try {
      await noteService.updateNote(note.id, {
        title: title || undefined,
        content,
        note_type: noteType
      })
      setHasChanges(false)
      message.success('已自动保存', 1)
    } catch (error) {
      console.error('自动保存失败:', error)
    }
  }

  // 手动保存
  const handleSave = async () => {
    if (!content || !content.trim()) {
      message.warning('请输入笔记内容')
      return
    }

    setSaving(true)
    try {
      const noteData = {
        title: title || undefined,
        content,
        note_type: noteType
      }

      let response
      if (note?.id) {
        // 更新现有笔记
        response = await noteService.updateNote(note.id, noteData)
      } else {
        // 创建新笔记
        response = await noteService.createNote(paperId, noteData)
      }

      if (response.code === 200) {
        message.success(note?.id ? '笔记更新成功' : '笔记创建成功')
        setHasChanges(false)
        if (onSave) {
          onSave(response.data)
        }
      } else {
        message.error(response.message || '保存失败')
      }
    } catch (error) {
      message.error('保存笔记失败: ' + (error.message || error))
    } finally {
      setSaving(false)
    }
  }

  // 组件卸载时清除定时器
  useEffect(() => {
    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current)
      }
    }
  }, [])

  // 离开前提示
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasChanges) {
        e.preventDefault()
        e.returnValue = '您有未保存的更改，确定要离开吗？'
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    }
  }, [hasChanges])

  return (
    <Card
      title={
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <span>{note?.id ? '编辑笔记' : '创建笔记'}</span>
          {hasChanges && <span style={{ color: '#faad14', fontSize: '12px' }}>未保存</span>}
        </Space>
      }
      extra={
        <Space>
          <Button onClick={onCancel}>取消</Button>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={saving}
          >
            保存
          </Button>
        </Space>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        {/* 笔记类型和标题 */}
        <Space style={{ width: '100%' }}>
          <Select
            value={noteType}
            onChange={(value) => {
              setNoteType(value)
              setHasChanges(true)
            }}
            style={{ width: 150 }}
          >
            {NOTE_TYPES.map(type => (
              <Option key={type.value} value={type.value}>
                {type.label}
              </Option>
            ))}
          </Select>

          {NOTE_TEMPLATES[noteType] && (
            <Button onClick={applyTemplate} size="small">
              应用{NOTE_TYPES.find(t => t.value === noteType)?.label}模板
            </Button>
          )}

          <Input
            placeholder="笔记标题（可选）"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value)
              setHasChanges(true)
            }}
            style={{ flex: 1 }}
            maxLength={200}
          />
        </Space>

        {/* Markdown编辑器 */}
        <MdEditor
          value={content}
          renderHTML={(text) => mdParser.render(text)}
          onChange={handleEditorChange}
          style={{ height: '500px' }}
          config={{
            view: {
              menu: true,
              md: true,
              html: true
            },
            canView: {
              menu: true,
              md: true,
              html: true,
              fullScreen: true,
              hideMenu: true
            }
          }}
          placeholder="请输入笔记内容（支持Markdown格式）"
        />

        <div style={{ fontSize: '12px', color: '#999' }}>
          提示：编辑器支持实时预览，30秒自动保存（仅更新已保存的笔记）
        </div>
      </Space>
    </Card>
  )
}

export default NoteEditor
