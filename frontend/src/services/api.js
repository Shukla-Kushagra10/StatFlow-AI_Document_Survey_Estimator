import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await axios.post(`${API_BASE_URL}/upload/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};

export const getProfile = async (datasetId) => {
  const res = await api.get(`/profile/${datasetId}`);
  return res.data;
};

export const cleanDataset = async (datasetId, operations) => {
  const res = await api.post('/clean/execute', { dataset_id: datasetId, operations });
  return res.data;
};

export const scanOutliers = async (datasetId, method = 'iqr') => {
  const res = await api.post('/outliers/scan', { dataset_id: datasetId, method });
  return res.data;
};

export const treatOutliers = async (datasetId, treatments) => {
  const res = await api.post('/outliers/treat', { dataset_id: datasetId, treatments });
  return res.data;
};

export const runValidation = async (datasetId) => {
  const res = await api.post('/validate/run', { dataset_id: datasetId });
  return res.data;
};

export const runPostStratification = async (datasetId, strataCol, popDist, baseWeightCol) => {
  const res = await api.post('/weighting/post-stratify', {
    dataset_id: datasetId,
    strata_col: strataCol,
    population_distribution: popDist,
    base_weight_col: baseWeightCol
  });
  return res.data;
};

export const computeEstimation = async (datasetId, targetCol, weightCol = 'survey_weight', confLevel = 0.95) => {
  const res = await api.post('/estimation/compute', {
    dataset_id: datasetId,
    target_column: targetCol,
    weight_column: weightCol,
    confidence_level: confLevel
  });
  return res.data;
};

export const getInsights = async (datasetId) => {
  const res = await api.get(`/insights/${datasetId}`);
  return res.data;
};

export const getAuditLogs = async (datasetId = null) => {
  const url = datasetId ? `/audit/?dataset_id=${datasetId}` : '/audit/';
  const res = await api.get(url);
  return res.data;
};

export const generateReport = async (datasetId, reportType = 'PDF', estimationData = null) => {
  const res = await api.post('/reports/generate', {
    dataset_id: datasetId,
    report_type: reportType,
    estimation_data: estimationData
  });
  return res.data;
};