import { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Table,
  Tag,
  DatePicker,
  Button,
  Space,
  Spin,
} from 'antd';
import {
  ExperimentOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  TrophyOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import { statisticsService } from '../services';
import type { StatisticsData, PerformanceTrendPoint } from '../types';

const { Title, Paragraph } = Typography;
const { RangePicker } = DatePicker;

function StatisticsPage() {
  const [loading, setLoading] = useState(true);
  const [statistics, setStatistics] = useState<StatisticsData | null>(null);
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(30, 'day'),
    dayjs(),
  ]);
  const [trendData, setTrendData] = useState<PerformanceTrendPoint[]>([]);
  const [trendLoading, setTrendLoading] = useState(false);

  const fetchStatistics = async () => {
    setLoading(true);
    try {
      const response = await statisticsService.getStatistics();
      setStatistics(response.data);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrend = async () => {
    setTrendLoading(true);
    try {
      const response = await statisticsService.getPerformanceTrend({
        start_date: dateRange[0].format('YYYY-MM-DD'),
        end_date: dateRange[1].format('YYYY-MM-DD'),
      });
      setTrendData(response.data);
    } catch (error) {
      console.error('Failed to fetch performance trend:', error);
    } finally {
      setTrendLoading(false);
    }
  };

  useEffect(() => {
    fetchStatistics();
    fetchTrend();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!statistics) {
    return <div>No statistics available</div>;
  }

  const trendColumns = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD'),
    },
    {
      title: '实验数量',
      dataIndex: 'experiment_count',
      key: 'experiment_count',
      sorter: (a: PerformanceTrendPoint, b: PerformanceTrendPoint) =>
        a.experiment_count - b.experiment_count,
    },
    {
      title: '最大浸出效率均值 (%)',
      dataIndex: 'max_leaching_efficiency_mean',
      key: 'max_leaching_efficiency_mean',
      render: (val?: number) =>
        val !== undefined && val !== null ? <Tag color="blue">{val.toFixed(2)}%</Tag> : <Tag>--</Tag>,
      sorter: (a: PerformanceTrendPoint, b: PerformanceTrendPoint) =>
        (a.max_leaching_efficiency_mean || 0) - (b.max_leaching_efficiency_mean || 0),
    },
    {
      title: '最大浸出效率中位数 (%)',
      dataIndex: 'max_leaching_efficiency_median',
      key: 'max_leaching_efficiency_median',
      render: (val?: number) =>
        val !== undefined && val !== null ? <Tag>{val.toFixed(2)}%</Tag> : <Tag>--</Tag>,
      sorter: (a: PerformanceTrendPoint, b: PerformanceTrendPoint) =>
        (a.max_leaching_efficiency_median || 0) - (b.max_leaching_efficiency_median || 0),
    },
    {
      title: '液体形成率',
      dataIndex: 'liquid_formation_rate',
      key: 'liquid_formation_rate',
      render: (val: number) => `${(val * 100).toFixed(1)}%`,
      sorter: (a: PerformanceTrendPoint, b: PerformanceTrendPoint) =>
        a.liquid_formation_rate - b.liquid_formation_rate,
    },
  ];

  const topFormulationColumns = [
    {
      title: '排名',
      key: 'rank',
      render: (_: unknown, __: unknown, index: number) => (
        <Tag color={index < 3 ? 'gold' : 'default'}>{index + 1}</Tag>
      ),
    },
    {
      title: '配方',
      dataIndex: 'formulation',
      key: 'formulation',
      render: (text: string) => <Typography.Text strong>{text}</Typography.Text>,
    },
    {
      title: '平均最大浸出效率 (%)',
      dataIndex: 'avg_max_leaching_efficiency',
      key: 'avg_max_leaching_efficiency',
      render: (val?: number) =>
        val !== undefined && val !== null ? <Tag color="blue">{val.toFixed(2)}%</Tag> : <Tag>--</Tag>,
    },
    {
      title: '成功次数',
      dataIndex: 'success_count',
      key: 'success_count',
    },
  ];

  const targetMaterialColumns = [
    { title: '目标物质', dataIndex: 'target_material', key: 'target_material' },
    { title: '实验数', dataIndex: 'experiments_total', key: 'experiments_total', sorter: (a: any, b: any) => a.experiments_total - b.experiments_total },
    { title: '形成率', dataIndex: 'liquid_formation_rate', key: 'liquid_formation_rate', render: (v: number) => `${(v * 100).toFixed(1)}%`, sorter: (a: any, b: any) => a.liquid_formation_rate - b.liquid_formation_rate },
    { title: '最大浸出效率均值 (%)', dataIndex: 'max_leaching_efficiency_mean', key: 'max_leaching_efficiency_mean', render: (v?: number) => v != null ? v.toFixed(2) : '--', sorter: (a: any, b: any) => (a.max_leaching_efficiency_mean || 0) - (b.max_leaching_efficiency_mean || 0) },
    { title: '最大浸出效率中位数 (%)', dataIndex: 'max_leaching_efficiency_median', key: 'max_leaching_efficiency_median', render: (v?: number) => v != null ? v.toFixed(2) : '--', sorter: (a: any, b: any) => (a.max_leaching_efficiency_median || 0) - (b.max_leaching_efficiency_median || 0) },
    { title: '最大浸出效率 P90 (%)', dataIndex: 'max_leaching_efficiency_p90', key: 'max_leaching_efficiency_p90', render: (v?: number) => v != null ? v.toFixed(2) : '--', sorter: (a: any, b: any) => (a.max_leaching_efficiency_p90 || 0) - (b.max_leaching_efficiency_p90 || 0) },
    { title: '平均测量条数', dataIndex: 'measurement_rows_mean', key: 'measurement_rows_mean', render: (v?: number) => v != null ? v.toFixed(2) : '--', sorter: (a: any, b: any) => (a.measurement_rows_mean || 0) - (b.measurement_rows_mean || 0) },
  ];

  return (
    <div>
      <Title level={2}>统计仪表板</Title>
      <Paragraph>
        系统性能概览和趋势分析
      </Paragraph>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总推荐数"
              value={statistics.summary.total_recommendations}
              prefix={<ExperimentOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="待实验"
              value={statistics.summary.pending_experiments}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已完成"
              value={statistics.summary.completed_experiments}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已取消"
              value={statistics.summary.cancelled}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12}>
          <Card>
            <Statistic
              title="液体形成成功率"
              value={(statistics.summary.liquid_formation_rate * 100).toFixed(1)}
              suffix="%"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card>
            <Statistic
              title="最大浸出效率均值"
              value={
                statistics.summary.max_leaching_efficiency_mean !== undefined &&
                statistics.summary.max_leaching_efficiency_mean !== null
                  ? statistics.summary.max_leaching_efficiency_mean.toFixed(2)
                  : '--'
              }
              suffix="%"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12}>
          <Card>
            <Statistic
              title="最大浸出效率中位数"
              value={
                statistics.summary.max_leaching_efficiency_median !== undefined &&
                statistics.summary.max_leaching_efficiency_median !== null
                  ? statistics.summary.max_leaching_efficiency_median.toFixed(2)
                  : '--'
              }
              suffix="%"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card>
            <Statistic
              title="平均测量条数"
              value={
                statistics.summary.measurement_rows_mean !== undefined &&
                statistics.summary.measurement_rows_mean !== null
                  ? statistics.summary.measurement_rows_mean.toFixed(2)
                  : '--'
              }
            />
          </Card>
        </Col>
      </Row>

      {/* By Material and By Status */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="按材料分布" bordered>
            {Object.entries(statistics.by_material)
              .sort(([, a], [, b]) => b - a)
              .map(([material, count]) => (
                <div
                  key={material}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginBottom: 12,
                  }}
                >
                  <Tag color="cyan">{material}</Tag>
                  <Typography.Text strong>{count} 个推荐</Typography.Text>
                </div>
              ))}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="按状态分布" bordered>
            {Object.entries(statistics.by_status).map(([status, count]) => {
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
              return (
                <div
                  key={status}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginBottom: 12,
                  }}
                >
                  <Tag color={colorMap[status]}>{labelMap[status]}</Tag>
                  <Typography.Text strong>{count} 个推荐</Typography.Text>
                </div>
              );
            })}
          </Card>
        </Col>
      </Row>

      {/* Target material stats */}
      <Card
        title="按目标物质统计（浸出效率）"
        style={{ marginBottom: 24 }}
      >
        <Table
          columns={targetMaterialColumns}
          dataSource={statistics.target_material_stats || []}
          rowKey="target_material"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Performance Trend */}
      <Card
        title="性能趋势"
        extra={
          <Space>
            <RangePicker
              value={dateRange}
              onChange={(dates) => {
                if (dates && dates[0] && dates[1]) {
                  setDateRange([dates[0], dates[1]]);
                }
              }}
            />
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              onClick={fetchTrend}
              loading={trendLoading}
            >
              刷新
            </Button>
          </Space>
        }
        style={{ marginBottom: 24 }}
      >
        <Table
          columns={trendColumns}
          dataSource={trendData}
          rowKey="date"
          loading={trendLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Top Formulations */}
      <Card
        title={
          <Space>
            <TrophyOutlined style={{ color: '#faad14' }} />
            <span>最佳配方 Top 10</span>
          </Space>
        }
      >
        <Table
          columns={topFormulationColumns}
          dataSource={statistics.top_formulations}
          rowKey="formulation"
          pagination={false}
        />
      </Card>
    </div>
  );
}

export default StatisticsPage;
