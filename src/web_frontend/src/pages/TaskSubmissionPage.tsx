import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Form,
  Input,
  InputNumber,
  Button,
  Card,
  Space,
  Typography,
  Divider,
  Table,
  Tag,
  message,
  Alert,
  Row,
  Col,
  Checkbox,
} from 'antd';
import { SendOutlined, ReloadOutlined } from '@ant-design/icons';
import { taskService } from '../services';
import type { TaskRequest } from '../types';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;

function TaskSubmissionPage() {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [submittedTasks, setSubmittedTasks] = useState<Array<{
    task_id: string;
    status: 'submitting' | 'success' | 'failed';
    message?: string;
    error?: string;
  }>>([]);
  const [batchMode, setBatchMode] = useState(false);

  const handleSubmit = async (values: TaskRequest & { batch_count?: number }) => {
    const batchCount = batchMode ? (values.batch_count || 1) : 1;

    // 批量提交任务
    const tasks = Array.from({ length: batchCount }, (_, index) => ({
      ...values,
      task_id: `${values.target_material}_${Date.now()}_${index + 1}`,
    }));

    // 初始化提交状态
    const taskStates = tasks.map((task) => ({
      task_id: task.task_id!,
      status: 'submitting' as const,
      message: '正在提交...',
    }));
    setSubmittedTasks(taskStates);

    // 异步提交所有任务（不阻塞UI）
    tasks.forEach(async (task, index) => {
      try {
        await taskService.createTask(task);

        // 更新状态为成功
        setSubmittedTasks((prev) =>
          prev.map((t) =>
            t.task_id === task.task_id
              ? { ...t, status: 'success', message: '提交成功，系统正在后台处理' }
              : t
          )
        );

        message.success(`任务 ${index + 1}/${batchCount} 提交成功`);
      } catch (error) {
        // 更新状态为失败
        setSubmittedTasks((prev) =>
          prev.map((t) =>
            t.task_id === task.task_id
              ? {
                  ...t,
                  status: 'failed',
                  message: '提交失败',
                  error: error instanceof Error ? error.message : '未知错误',
                }
              : t
          )
        );

        message.error(`任务 ${index + 1}/${batchCount} 提交失败`);
      }
    });

    message.info(
      `已提交 ${batchCount} 个任务，系统将在后台处理。您可以前往推荐列表查看进度。`
    );
  };

  const taskColumns = [
    {
      title: '任务ID',
      dataIndex: 'task_id',
      key: 'task_id',
      render: (id: string) => <Text code>{id.slice(0, 20)}...</Text>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colorMap = {
          submitting: 'blue',
          success: 'green',
          failed: 'red',
        };
        const labelMap = {
          submitting: '提交中',
          success: '成功',
          failed: '失败',
        };
        return <Tag color={colorMap[status as keyof typeof colorMap]}>{labelMap[status as keyof typeof labelMap]}</Tag>;
      },
    },
    {
      title: '消息',
      dataIndex: 'message',
      key: 'message',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: any) => (
        record.status === 'success' ? (
          <Button
            type="link"
            size="small"
            onClick={() => navigate('/recommendations')}
          >
            查看推荐列表
          </Button>
        ) : null
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>任务提交</Title>
      <Paragraph>
        提交您的DES配方需求，系统将在后台生成推荐配方。任务提交后不会阻塞页面，您可以继续操作。
      </Paragraph>

      <Alert
        message="提示"
        description="任务提交后系统将在后台处理（可能需要几分钟），您可以前往推荐列表查看生成的推荐配方。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Card title="配方需求" style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            target_temperature: 25.0,
            num_components: 2,
            batch_count: 1,
          }}
        >
          <Form.Item
            label="任务描述"
            name="description"
            rules={[
              { required: true, message: '请输入任务描述' },
              { min: 10, message: '描述至少10个字符' },
            ]}
          >
            <TextArea
              rows={4}
              placeholder="例如: 设计一种可以在-20°C下溶解纤维素的DES配方"
              showCount
              maxLength={500}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="目标材料"
                name="target_material"
                rules={[{ required: true, message: '请输入目标材料' }]}
              >
                <Input placeholder="例如: cellulose, lignin, chitin" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="目标温度 (°C)"
                name="target_temperature"
                rules={[{ required: true, message: '请输入目标温度' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={-80}
                  max={150}
                  step={0.1}
                  placeholder="例如: -20.0"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="组分数量"
            name="num_components"
            tooltip="DES的组分数量：2=二元(Binary), 3=三元(Ternary), 4=四元(Quaternary), 5+=多元(Multi-component)"
            rules={[
              { required: true, message: '请输入组分数量' },
              { type: 'number', min: 2, max: 10, message: '组分数量范围: 2-10' },
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={2}
              max={10}
              step={1}
              placeholder="输入组分数量 (2-10)"
            />
          </Form.Item>

          <Form.Item label="约束条件 (可选)" name="constraints">
            <TextArea
              rows={3}
              placeholder="例如: 无毒性, 成本低于10元/kg"
            />
          </Form.Item>

          <Divider />

          <Form.Item>
            <Checkbox
              checked={batchMode}
              onChange={(e) => setBatchMode(e.target.checked)}
            >
              批量提交模式
            </Checkbox>
          </Form.Item>

          {batchMode && (
            <Form.Item
              label="提交数量"
              name="batch_count"
              rules={[
                { required: true, message: '请输入提交数量' },
                { type: 'number', min: 1, max: 10, message: '数量范围: 1-10' },
              ]}
            >
              <InputNumber
                style={{ width: '100%' }}
                min={1}
                max={10}
                placeholder="输入要提交的任务数量 (1-10)"
              />
            </Form.Item>
          )}

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SendOutlined />}
                size="large"
              >
                {batchMode ? '批量提交任务' : '提交任务'}
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => form.resetFields()}
              >
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {submittedTasks.length > 0 && (
        <>
          <Divider />
          <Title level={3}>提交状态 ({submittedTasks.length} 个任务)</Title>
          <Paragraph>
            任务已提交到后台队列，系统正在处理。您可以前往
            <Button
              type="link"
              onClick={() => navigate('/recommendations')}
              style={{ padding: '0 4px' }}
            >
              推荐列表
            </Button>
            查看生成的配方。
          </Paragraph>
          <Table
            columns={taskColumns}
            dataSource={submittedTasks}
            rowKey="task_id"
            pagination={false}
            size="small"
          />
        </>
      )}
    </div>
  );
}

export default TaskSubmissionPage;
