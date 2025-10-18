import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  Typography,
  Divider,
  Alert,
  Spin,
  Progress,
  List,
} from 'antd';
import {
  ArrowLeftOutlined,
  ExperimentOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { recommendationService } from '../services';
import type { RecommendationDetail } from '../types';

const { Title, Paragraph, Text } = Typography;

function RecommendationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState<RecommendationDetail | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchDetail = async () => {
      setLoading(true);
      try {
        const response = await recommendationService.getRecommendationDetail(id);
        setDetail(response.data);
      } catch (error) {
        console.error('Failed to fetch recommendation detail:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();
  }, [id]);

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

  const statusColorMap: Record<string, string> = {
    PENDING: 'orange',
    COMPLETED: 'green',
    CANCELLED: 'red',
  };

  const statusLabelMap: Record<string, string> = {
    PENDING: '待实验',
    COMPLETED: '已完成',
    CANCELLED: '已取消',
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/recommendations')}
        >
          返回列表
        </Button>
        {detail.status === 'PENDING' && (
          <Button
            type="primary"
            icon={<ExperimentOutlined />}
            onClick={() => navigate(`/feedback/${detail.recommendation_id}`)}
          >
            提交实验反馈
          </Button>
        )}
      </Space>

      <Card>
        <Title level={2}>
          {detail.formulation.HBD} : {detail.formulation.HBA} ({detail.formulation.molar_ratio})
        </Title>
        <Tag color={statusColorMap[detail.status]} style={{ marginBottom: 16 }}>
          {statusLabelMap[detail.status]}
        </Tag>

        <Descriptions bordered column={2}>
          <Descriptions.Item label="推荐ID" span={2}>
            <Text code>{detail.recommendation_id}</Text>
          </Descriptions.Item>
          <Descriptions.Item label="目标材料">
            <Tag color="cyan">{detail.task.target_material}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="目标温度">
            {detail.task.target_temperature}°C
          </Descriptions.Item>
          <Descriptions.Item label="HBD (氢键供体)">
            <Tag color="blue">{detail.formulation.HBD}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="HBA (氢键受体)">
            <Tag color="green">{detail.formulation.HBA}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="摩尔比">
            {detail.formulation.molar_ratio}
          </Descriptions.Item>
          <Descriptions.Item label="置信度">
            <Progress
              percent={Math.round(detail.confidence * 100)}
              size="small"
              style={{ width: 200 }}
            />
          </Descriptions.Item>
          <Descriptions.Item label="创建时间" span={2}>
            {dayjs(detail.created_at).format('YYYY-MM-DD HH:mm:ss')}
          </Descriptions.Item>
          {detail.updated_at && (
            <Descriptions.Item label="更新时间" span={2}>
              {dayjs(detail.updated_at).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
          )}
        </Descriptions>

        <Divider orientation="left">推理过程</Divider>
        <Card type="inner">
          <Paragraph style={{ whiteSpace: 'pre-wrap' }}>
            {detail.reasoning}
          </Paragraph>
        </Card>

        {detail.supporting_evidence && detail.supporting_evidence.length > 0 && (
          <>
            <Divider orientation="left">支持证据</Divider>
            <List
              dataSource={detail.supporting_evidence}
              renderItem={(evidence, index) => (
                <List.Item>
                  <Text>[{index + 1}] {evidence}</Text>
                </List.Item>
              )}
            />
          </>
        )}

        <Divider orientation="left">生成轨迹</Divider>
        <Card type="inner">
          <List
            dataSource={detail.trajectory.steps}
            renderItem={(step, index) => (
              <List.Item>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>步骤 {index + 1}: {step.action}</Text>
                  <Paragraph style={{ marginLeft: 16, marginBottom: 0 }}>
                    {step.reasoning}
                  </Paragraph>
                  {step.tool && (
                    <Tag color="purple">工具: {step.tool}</Tag>
                  )}
                </Space>
              </List.Item>
            )}
          />
        </Card>

        {detail.experiment_result && (
          <>
            <Divider orientation="left">实验结果</Divider>
            <Alert
              message={
                detail.experiment_result.is_liquid_formed
                  ? '液体形成成功'
                  : '液体形成失败'
              }
              type={detail.experiment_result.is_liquid_formed ? 'success' : 'error'}
              icon={
                detail.experiment_result.is_liquid_formed ? (
                  <CheckCircleOutlined />
                ) : (
                  <CloseCircleOutlined />
                )
              }
              showIcon
              style={{ marginBottom: 16 }}
            />
            <Descriptions bordered column={2}>
              {detail.experiment_result.solubility !== undefined && (
                <Descriptions.Item label="溶解度">
                  {detail.experiment_result.solubility}{' '}
                  {detail.experiment_result.solubility_unit}
                </Descriptions.Item>
              )}
              <Descriptions.Item label="性能得分">
                <Progress
                  percent={detail.experiment_result.performance_score * 10}
                  size="small"
                  style={{ width: 200 }}
                />
                <Text> {detail.experiment_result.performance_score.toFixed(1)}/10</Text>
              </Descriptions.Item>
              {detail.experiment_result.experimenter && (
                <Descriptions.Item label="实验人员">
                  {detail.experiment_result.experimenter}
                </Descriptions.Item>
              )}
              {detail.experiment_result.properties &&
                Object.keys(detail.experiment_result.properties).length > 0 && (
                  <Descriptions.Item label="其他性质" span={2}>
                    {Object.entries(detail.experiment_result.properties).map(
                      ([key, value]) => (
                        <Tag key={key}>
                          {key}: {String(value)}
                        </Tag>
                      )
                    )}
                  </Descriptions.Item>
                )}
              {detail.experiment_result.notes && (
                <Descriptions.Item label="备注" span={2}>
                  {detail.experiment_result.notes}
                </Descriptions.Item>
              )}
              <Descriptions.Item label="实验日期" span={2}>
                {dayjs(detail.experiment_result.experiment_date).format(
                  'YYYY-MM-DD HH:mm:ss'
                )}
              </Descriptions.Item>
            </Descriptions>
          </>
        )}
      </Card>
    </div>
  );
}

export default RecommendationDetailPage;
