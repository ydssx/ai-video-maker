import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Progress, Tag, Alert } from 'antd';
import { 
  FileTextOutlined, 
  VideoCameraOutlined, 
  ClockCircleOutlined,
  TrophyOutlined,
  WarningOutlined
} from '@ant-design/icons';
import axios from 'axios';

function UserDashboard() {
  const [userStats, setUserStats] = useState(null);
  const [userQuota, setUserQuota] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const [statsResponse, quotaResponse] = await Promise.all([
        axios.get('/api/stats/user-stats'),
        axios.get('/api/stats/user-quota')
      ]);
      
      setUserStats(statsResponse.data.stats);
      setUserQuota(quotaResponse.data.quota);
    } catch (error) {
      console.error('获取用户数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>加载中...</div>;
  }

  const getQuotaStatus = (used, total) => {
    const percentage = (used / total) * 100;
    if (percentage >= 90) return 'exception';
    if (percentage >= 70) return 'active';
    return 'success';
  };

  const getQuotaColor = (used, total) => {
    const percentage = (used / total) * 100;
    if (percentage >= 90) return '#ff4d4f';
    if (percentage >= 70) return '#faad14';
    return '#52c41a';
  };

  return (
    <div style={{ padding: '20px 0' }}>
      <Row gutter={[16, 16]}>
        {/* 使用统计 */}
        <Col span={24}>
          <Card title="📊 使用统计" size="small">
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="生成脚本"
                  value={userStats?.scripts_generated || 0}
                  prefix={<FileTextOutlined />}
                  suffix="个"
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="制作视频"
                  value={userStats?.videos_created || 0}
                  prefix={<VideoCameraOutlined />}
                  suffix="个"
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="总时长"
                  value={userStats?.total_duration || 0}
                  prefix={<ClockCircleOutlined />}
                  suffix="秒"
                  precision={1}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 今日配额 */}
        <Col span={12}>
          <Card title="📅 今日配额" size="small">
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span>脚本生成</span>
                <span>
                  {userQuota?.used_today_scripts || 0} / {userQuota?.daily_scripts || 10}
                </span>
              </div>
              <Progress
                percent={((userQuota?.used_today_scripts || 0) / (userQuota?.daily_scripts || 10)) * 100}
                status={getQuotaStatus(userQuota?.used_today_scripts || 0, userQuota?.daily_scripts || 10)}
                strokeColor={getQuotaColor(userQuota?.used_today_scripts || 0, userQuota?.daily_scripts || 10)}
                size="small"
              />
            </div>
            
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span>视频制作</span>
                <span>
                  {userQuota?.used_today_videos || 0} / {userQuota?.daily_videos || 5}
                </span>
              </div>
              <Progress
                percent={((userQuota?.used_today_videos || 0) / (userQuota?.daily_videos || 5)) * 100}
                status={getQuotaStatus(userQuota?.used_today_videos || 0, userQuota?.daily_videos || 5)}
                strokeColor={getQuotaColor(userQuota?.used_today_videos || 0, userQuota?.daily_videos || 5)}
                size="small"
              />
            </div>
          </Card>
        </Col>

        {/* 月度配额 */}
        <Col span={12}>
          <Card title="📆 月度配额" size="small">
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span>脚本生成</span>
                <span>
                  {userQuota?.used_month_scripts || 0} / {userQuota?.monthly_scripts || 100}
                </span>
              </div>
              <Progress
                percent={((userQuota?.used_month_scripts || 0) / (userQuota?.monthly_scripts || 100)) * 100}
                status={getQuotaStatus(userQuota?.used_month_scripts || 0, userQuota?.monthly_scripts || 100)}
                strokeColor={getQuotaColor(userQuota?.used_month_scripts || 0, userQuota?.monthly_scripts || 100)}
                size="small"
              />
            </div>
            
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span>视频制作</span>
                <span>
                  {userQuota?.used_month_videos || 0} / {userQuota?.monthly_videos || 50}
                </span>
              </div>
              <Progress
                percent={((userQuota?.used_month_videos || 0) / (userQuota?.monthly_videos || 50)) * 100}
                status={getQuotaStatus(userQuota?.used_month_videos || 0, userQuota?.monthly_videos || 50)}
                strokeColor={getQuotaColor(userQuota?.used_month_videos || 0, userQuota?.monthly_videos || 50)}
                size="small"
              />
            </div>
          </Card>
        </Col>

        {/* 配额警告 */}
        {((userQuota?.used_today_scripts || 0) >= (userQuota?.daily_scripts || 10) * 0.8 ||
          (userQuota?.used_today_videos || 0) >= (userQuota?.daily_videos || 5) * 0.8) && (
          <Col span={24}>
            <Alert
              message="配额提醒"
              description={
                <div>
                  {(userQuota?.used_today_scripts || 0) >= (userQuota?.daily_scripts || 10) * 0.8 && (
                    <div>• 今日脚本生成配额即将用完</div>
                  )}
                  {(userQuota?.used_today_videos || 0) >= (userQuota?.daily_videos || 5) * 0.8 && (
                    <div>• 今日视频制作配额即将用完</div>
                  )}
                  <div style={{ marginTop: 8, fontSize: '12px', color: '#666' }}>
                    配额每日 00:00 重置，升级账户可获得更多配额
                  </div>
                </div>
              }
              type="warning"
              icon={<WarningOutlined />}
              showIcon
            />
          </Col>
        )}

        {/* 成就系统 */}
        <Col span={24}>
          <Card title="🏆 成就徽章" size="small">
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {(userStats?.scripts_generated || 0) >= 1 && (
                <Tag color="blue" icon={<FileTextOutlined />}>首次创作</Tag>
              )}
              {(userStats?.scripts_generated || 0) >= 10 && (
                <Tag color="green" icon={<FileTextOutlined />}>创作达人</Tag>
              )}
              {(userStats?.videos_created || 0) >= 1 && (
                <Tag color="purple" icon={<VideoCameraOutlined />}>视频新手</Tag>
              )}
              {(userStats?.videos_created || 0) >= 5 && (
                <Tag color="orange" icon={<VideoCameraOutlined />}>视频制作者</Tag>
              )}
              {(userStats?.total_duration || 0) >= 300 && (
                <Tag color="red" icon={<TrophyOutlined />}>时长大师</Tag>
              )}
              {((userStats?.scripts_generated || 0) === 0 && (userStats?.videos_created || 0) === 0) && (
                <span style={{ color: '#999', fontSize: '12px' }}>
                  开始创作来解锁成就徽章吧！
                </span>
              )}
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default UserDashboard;