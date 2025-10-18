import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Form,
  Input,
  InputNumber,
  Button,
  Card,
  Space,
  Typography,
  Radio,
  Alert,
  Spin,
  message,
  Divider,
} from 'antd';
import { ArrowLeftOutlined, SendOutlined } from '@ant-design/icons';
import { feedbackService, recommendationService } from '../services';
import type { ExperimentResultRequest, RecommendationDetail } from '../types';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;

function FeedbackPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [detail, setDetail] = useState<RecommendationDetail | null>(null);
  const [isLiquidFormed, setIsLiquidFormed] = useState<boolean>(true);

  useEffect(() => {
    if (!id) return;

    const fetchDetail = async () => {
      setLoading(true);
      try {
        const response = await recommendationService.getRecommendationDetail(id);
        setDetail(response.data);

        // Check if already has experiment result
        if (response.data.experiment_result) {
          message.warning('该推荐已经提交过实验反馈');
        }
      } catch (error) {
        console.error('Failed to fetch recommendation detail:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();
  }, [id]);

  const handleSubmit = async (values: ExperimentResultRequest) => {
    if (!id) return;

    setSubmitting(true);
    try {
      const response = await feedbackService.submitFeedback({
        recommendation_id: id,
        experiment_result: values,
      });

      message.success(response.message);
      // Navigate to detail page
      navigate(`/recommendations/${id}`);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!detail) {
    return (
      <Alert
        message="推荐不存在"
        description="未找到该推荐信息"
        type="error"
        showIcon
      />
    );
  }

  if (detail.status !== 'PENDING') {
    return (
      <Alert
        message="无法提交反馈"
        description={`该推荐的状态为 ${detail.status}，只有待实验状态的推荐才能提交反馈`}
        type="warning"
        showIcon
      />
    );
  }

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(`/recommendations/${id}`)}
        >
          返回详情
        </Button>
      </Space>

      <Title level={2}>提交实验反馈</Title>
      <Paragraph>
        请填写您的实验结果，系统将自动学习并优化未来的推荐。
      </Paragraph>

      <Card title="推荐配方信息" style={{ marginBottom: 24 }}>
        <Paragraph>
          <Text strong>配方:</Text> {detail.formulation.HBD} : {detail.formulation.HBA} ({detail.formulation.molar_ratio})
        </Paragraph>
        <Paragraph>
          <Text strong>目标材料:</Text> {detail.task.target_material}
        </Paragraph>
        <Paragraph>
          <Text strong>目标温度:</Text> {detail.task.target_temperature}°C
        </Paragraph>
      </Card>

      <Card title="实验结果">
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            is_liquid_formed: true,
            solubility_unit: 'g/L',
          }}
        >
          <Form.Item
            label="DES液体是否成功形成？"
            name="is_liquid_formed"
            rules={[{ required: true, message: '请选择液体是否形成' }]}
          >
            <Radio.Group onChange={(e) => setIsLiquidFormed(e.target.value)}>
              <Radio value={true}>是</Radio>
              <Radio value={false}>否</Radio>
            </Radio.Group>
          </Form.Item>

          {!isLiquidFormed && (
            <Alert
              message="液体未形成"
              description="如果DES液体未能成功形成，请在备注中说明原因（如固体未溶解、分层等）"
              type="warning"
              showIcon
              style={{ marginBottom: 16 }}
            />
          )}

          {isLiquidFormed && (
            <>
              <Form.Item
                label="溶解度"
                name="solubility"
                rules={[
                  {
                    required: isLiquidFormed,
                    message: '液体形成时必须填写溶解度',
                  },
                  { type: 'number', min: 0, message: '溶解度必须为正数' },
                ]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  step={0.1}
                  placeholder="例如: 8.5"
                  addonAfter={
                    <Form.Item name="solubility_unit" noStyle>
                      <Input style={{ width: 80 }} placeholder="g/L" />
                    </Form.Item>
                  }
                />
              </Form.Item>
            </>
          )}

          <Form.Item
            label="实验温度 (°C)"
            name="temperature"
          >
            <InputNumber
              style={{ width: '100%' }}
              min={-80}
              max={150}
              step={0.1}
              placeholder="实际实验温度"
            />
          </Form.Item>

          <Divider orientation="left">其他性质（可选）</Divider>

          <Form.Item label="其他观察到的性质" help="每行一个属性，格式: 属性名=值">
            <TextArea
              rows={4}
              placeholder="例如:
viscosity=low
color=transparent
stability=good"
              onChange={(e) => {
                const text = e.target.value;
                if (!text) {
                  form.setFieldValue('properties', undefined);
                  return;
                }

                const properties: Record<string, string> = {};
                const lines = text.split('\n');
                for (const line of lines) {
                  const [key, value] = line.split('=').map((s) => s.trim());
                  if (key && value) {
                    properties[key] = value;
                  }
                }
                form.setFieldValue('properties', properties);
              }}
            />
          </Form.Item>

          <Form.Item name="properties" hidden>
            <Input />
          </Form.Item>

          <Form.Item label="备注" name="notes">
            <TextArea
              rows={3}
              placeholder="请记录实验过程中的任何额外观察、问题或建议"
              showCount
              maxLength={500}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SendOutlined />}
                loading={submitting}
                size="large"
              >
                提交反馈
              </Button>
              <Button
                onClick={() => navigate(`/recommendations/${id}`)}
                size="large"
              >
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}

export default FeedbackPage;
