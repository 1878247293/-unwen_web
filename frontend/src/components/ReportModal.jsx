import React, { useState } from 'react'
import { Modal, Select, Input, message } from 'antd'
import discussionService from '../services/discussionService'

const { TextArea } = Input
const { Option } = Select

const ReportModal = ({ visible, onClose, discussionId, onReportSubmitted }) => {
  const [reason, setReason] = useState('')
  const [description, setDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const reportReasons = [
    { value: '垃圾广告', label: '垃圾广告' },
    { value: '不当言论', label: '不当言论' },
    { value: '虚假信息', label: '虚假信息' },
    { value: '其他', label: '其他' }
  ]

  const handleSubmit = async () => {
    if (!reason) {
      message.warning('请选择举报原因')
      return
    }

    if (!description.trim()) {
      message.warning('请填写详细说明')
      return
    }

    setSubmitting(true)
    try {
      const response = await discussionService.reportDiscussion(discussionId, {
        reason: `${reason}: ${description.trim()}`
      })

      if (response.code === 200) {
        message.success('举报已提交，感谢您的反馈')
        setReason('')
        setDescription('')
        if (onReportSubmitted) {
          onReportSubmitted()
        }
        onClose()
      } else {
        message.error(response.message || '举报提交失败')
      }
    } catch (error) {
      message.error('举报提交失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSubmitting(false)
    }
  }

  const handleCancel = () => {
    setReason('')
    setDescription('')
    onClose()
  }

  return (
    <Modal
      title="举报讨论"
      open={visible}
      onOk={handleSubmit}
      onCancel={handleCancel}
      okText="提交举报"
      cancelText="取消"
      confirmLoading={submitting}
      width={500}
    >
      <div>
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            举报原因 <span style={{ color: 'red' }}>*</span>
          </label>
          <Select
            placeholder="请选择举报原因"
            value={reason}
            onChange={setReason}
            style={{ width: '100%' }}
          >
            {reportReasons.map((item) => (
              <Option key={item.value} value={item.value}>
                {item.label}
              </Option>
            ))}
          </Select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            详细说明 <span style={{ color: 'red' }}>*</span>
          </label>
          <TextArea
            placeholder="请详细描述举报原因..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={6}
            maxLength={1000}
            showCount
          />
        </div>
      </div>
    </Modal>
  )
}

export default ReportModal
