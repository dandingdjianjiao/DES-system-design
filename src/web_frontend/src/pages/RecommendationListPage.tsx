import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table,
  Typography,
  Tag,
  Button,
  Space,
  Select,
  Input,
  Card,
  message,
} from 'antd';
import { EyeOutlined, ExperimentOutlined, ReloadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { recommendationService } from '../services';
import type { RecommendationSummary, FormulationData } from '../types';
import { getFormulationDisplayString } from '../utils/formulationUtils';

const { Title, Paragraph } = Typography;
const { Search } = Input;

function RecommendationListPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<RecommendationSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [materialFilter, setMaterialFilter] = useState<string | undefined>(undefined);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const response = await recommendationService.listRecommendations({
        status: statusFilter as any,
        material: materialFilter,
        page: currentPage,
        page_size: pageSize,
      });
      setRecommendations(response.data.items);
      setTotal(response.data.pagination.total);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [currentPage, pageSize, statusFilter, materialFilter]);

  const columns = [
    {
      title: '推荐ID',
      dataIndex: 'recommendation_id',
      key: 'recommendation_id',
      width: 120,
      render: (id: string) => (
        <Typography.Text code>{id.slice(0, 8)}</Typography.Text>
      ),
    },
    {
      title: '配方',
      dataIndex: 'formulation',
      key: 'formulation',
      render: (formulation: FormulationData) => (
        <Typography.Text strong>
          {getFormulationDisplayString(formulation)}
        </Typography.Text>
      ),
    },
    {
      title: '目标材料',
      dataIndex: 'target_material',
      key: 'target_material',
      render: (material: string) => <Tag color="cyan">{material}</Tag>,
    },
    {
      title: '目标温度',
      dataIndex: 'target_temperature',
      key: 'target_temperature',
      render: (temp: number) => `${temp}°C`,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          PENDING: 'orange',
          COMPLETED: 'green',
          CANCELLED: 'red',
        };
        const labelMap: Record<string, string> = {
          PENDING: '待实验',
          COMPLETED: '已完成',
          CANCELLED: '已取消',
        };
        return <Tag color={colorMap[status]}>{labelMap[status]}</Tag>;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right' as const,
      width: 180,
      render: (_: unknown, record: RecommendationSummary) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/recommendations/${record.recommendation_id}`)}
          >
            详情
          </Button>
          {record.status === 'PENDING' && (
            <Button
              type="link"
              icon={<ExperimentOutlined />}
              onClick={() => navigate(`/feedback/${record.recommendation_id}`)}
            >
              反馈
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>推荐列表</Title>
      <Paragraph>
        查看所有DES配方推荐，可按状态和材料筛选。
      </Paragraph>

      <Card style={{ marginBottom: 16 }}>
        <Space size="middle" wrap>
          <span>状态筛选:</span>
          <Select
            style={{ width: 150 }}
            placeholder="选择状态"
            allowClear
            value={statusFilter}
            onChange={(value) => {
              setStatusFilter(value);
              setCurrentPage(1);
            }}
            options={[
              { label: '待实验', value: 'PENDING' },
              { label: '已完成', value: 'COMPLETED' },
              { label: '已取消', value: 'CANCELLED' },
            ]}
          />

          <span>材料筛选:</span>
          <Search
            placeholder="输入材料名称"
            allowClear
            style={{ width: 200 }}
            onSearch={(value) => {
              setMaterialFilter(value || undefined);
              setCurrentPage(1);
            }}
          />

          <Button
            icon={<ReloadOutlined />}
            onClick={() => {
              setStatusFilter(undefined);
              setMaterialFilter(undefined);
              setCurrentPage(1);
              fetchRecommendations();
            }}
          >
            重置
          </Button>

          <Button
            type="primary"
            onClick={fetchRecommendations}
          >
            刷新
          </Button>
        </Space>
      </Card>

      <Table
        columns={columns}
        dataSource={recommendations}
        rowKey="recommendation_id"
        loading={loading}
        scroll={{ x: 1200 }}
        pagination={{
          current: currentPage,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, size) => {
            setCurrentPage(page);
            setPageSize(size);
          },
        }}
      />
    </div>
  );
}

export default RecommendationListPage;
