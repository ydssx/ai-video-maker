import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { message } from 'antd';

// 创建上下文
const AppContext = createContext();

// 初始状态
const initialState = {
  // 用户数据
  user: {
    name: '用户',
    avatar: null,
    preferences: {
      theme: 'light',
      language: 'zh-CN',
      autoSave: true
    }
  },
  
  // 应用状态
  app: {
    currentStep: 0,
    loading: false,
    error: null,
    notifications: []
  },
  
  // 项目数据
  project: {
    id: null,
    name: '',
    script: null,
    videoConfig: {
      template: 'modern',
      resolution: '1080p',
      fps: 30,
      format: 'mp4'
    },
    videoId: null,
    lastSaved: null,
    isDirty: false
  },
  
  // 编辑器状态
  editor: {
    activeTab: 'preview',
    timeline: {
      currentTime: 0,
      duration: 0,
      playing: false
    },
    textStyle: {
      fontFamily: 'Arial',
      fontSize: 24,
      color: '#ffffff',
      position: 'center',
      animation: 'fadeIn'
    },
    assets: [],
    selectedAssets: []
  },
  
  // 预览状态
  preview: {
    url: null,
    thumbnail: null,
    status: 'idle', // idle, generating, ready, error
    progress: 0
  }
};

// Action 类型
export const ActionTypes = {
  // 应用状态
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_CURRENT_STEP: 'SET_CURRENT_STEP',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  
  // 项目管理
  SET_PROJECT: 'SET_PROJECT',
  UPDATE_PROJECT: 'UPDATE_PROJECT',
  SET_SCRIPT: 'SET_SCRIPT',
  SET_VIDEO_CONFIG: 'SET_VIDEO_CONFIG',
  SET_VIDEO_ID: 'SET_VIDEO_ID',
  MARK_PROJECT_DIRTY: 'MARK_PROJECT_DIRTY',
  MARK_PROJECT_CLEAN: 'MARK_PROJECT_CLEAN',
  
  // 编辑器状态
  SET_ACTIVE_TAB: 'SET_ACTIVE_TAB',
  UPDATE_TIMELINE: 'UPDATE_TIMELINE',
  UPDATE_TEXT_STYLE: 'UPDATE_TEXT_STYLE',
  SET_ASSETS: 'SET_ASSETS',
  ADD_ASSET: 'ADD_ASSET',
  REMOVE_ASSET: 'REMOVE_ASSET',
  SELECT_ASSETS: 'SELECT_ASSETS',
  
  // 预览状态
  UPDATE_PREVIEW: 'UPDATE_PREVIEW',
  SET_PREVIEW_STATUS: 'SET_PREVIEW_STATUS',
  SET_PREVIEW_PROGRESS: 'SET_PREVIEW_PROGRESS',
  
  // 用户设置
  UPDATE_USER_PREFERENCES: 'UPDATE_USER_PREFERENCES'
};

// Reducer 函数
const appReducer = (state, action) => {
  switch (action.type) {
    case ActionTypes.SET_LOADING:
      return {
        ...state,
        app: { ...state.app, loading: action.payload }
      };
      
    case ActionTypes.SET_ERROR:
      return {
        ...state,
        app: { ...state.app, error: action.payload }
      };
      
    case ActionTypes.CLEAR_ERROR:
      return {
        ...state,
        app: { ...state.app, error: null }
      };
      
    case ActionTypes.SET_CURRENT_STEP:
      return {
        ...state,
        app: { ...state.app, currentStep: action.payload }
      };
      
    case ActionTypes.ADD_NOTIFICATION:
      return {
        ...state,
        app: {
          ...state.app,
          notifications: [...state.app.notifications, action.payload]
        }
      };
      
    case ActionTypes.REMOVE_NOTIFICATION:
      return {
        ...state,
        app: {
          ...state.app,
          notifications: state.app.notifications.filter(n => n.id !== action.payload)
        }
      };
      
    case ActionTypes.SET_PROJECT:
      return {
        ...state,
        project: { ...action.payload, isDirty: false }
      };
      
    case ActionTypes.UPDATE_PROJECT:
      return {
        ...state,
        project: { ...state.project, ...action.payload, isDirty: true }
      };
      
    case ActionTypes.SET_SCRIPT:
      return {
        ...state,
        project: { ...state.project, script: action.payload, isDirty: true }
      };
      
    case ActionTypes.SET_VIDEO_CONFIG:
      return {
        ...state,
        project: {
          ...state.project,
          videoConfig: { ...state.project.videoConfig, ...action.payload },
          isDirty: true
        }
      };
      
    case ActionTypes.SET_VIDEO_ID:
      return {
        ...state,
        project: { ...state.project, videoId: action.payload }
      };
      
    case ActionTypes.MARK_PROJECT_DIRTY:
      return {
        ...state,
        project: { ...state.project, isDirty: true }
      };
      
    case ActionTypes.MARK_PROJECT_CLEAN:
      return {
        ...state,
        project: { ...state.project, isDirty: false, lastSaved: new Date().toISOString() }
      };
      
    case ActionTypes.SET_ACTIVE_TAB:
      return {
        ...state,
        editor: { ...state.editor, activeTab: action.payload }
      };
      
    case ActionTypes.UPDATE_TIMELINE:
      return {
        ...state,
        editor: {
          ...state.editor,
          timeline: { ...state.editor.timeline, ...action.payload }
        }
      };
      
    case ActionTypes.UPDATE_TEXT_STYLE:
      return {
        ...state,
        editor: {
          ...state.editor,
          textStyle: { ...state.editor.textStyle, ...action.payload }
        }
      };
      
    case ActionTypes.SET_ASSETS:
      return {
        ...state,
        editor: { ...state.editor, assets: action.payload }
      };
      
    case ActionTypes.ADD_ASSET:
      return {
        ...state,
        editor: {
          ...state.editor,
          assets: [...state.editor.assets, action.payload]
        }
      };
      
    case ActionTypes.REMOVE_ASSET:
      return {
        ...state,
        editor: {
          ...state.editor,
          assets: state.editor.assets.filter(asset => asset.id !== action.payload),
          selectedAssets: state.editor.selectedAssets.filter(id => id !== action.payload)
        }
      };
      
    case ActionTypes.SELECT_ASSETS:
      return {
        ...state,
        editor: { ...state.editor, selectedAssets: action.payload }
      };
      
    case ActionTypes.UPDATE_PREVIEW:
      return {
        ...state,
        preview: { ...state.preview, ...action.payload }
      };
      
    case ActionTypes.SET_PREVIEW_STATUS:
      return {
        ...state,
        preview: { ...state.preview, status: action.payload }
      };
      
    case ActionTypes.SET_PREVIEW_PROGRESS:
      return {
        ...state,
        preview: { ...state.preview, progress: action.payload }
      };
      
    case ActionTypes.UPDATE_USER_PREFERENCES:
      return {
        ...state,
        user: {
          ...state.user,
          preferences: { ...state.user.preferences, ...action.payload }
        }
      };
      
    default:
      return state;
  }
};

// Context Provider 组件
export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);
  
  // 自动保存功能
  useEffect(() => {
    if (state.project.isDirty && state.user.preferences.autoSave) {
      const timer = setTimeout(() => {
        // 这里可以调用保存API
        console.log('自动保存项目...');
        dispatch({ type: ActionTypes.MARK_PROJECT_CLEAN });
      }, 5000); // 5秒后自动保存
      
      return () => clearTimeout(timer);
    }
  }, [state.project.isDirty, state.user.preferences.autoSave]);
  
  // 错误处理
  useEffect(() => {
    if (state.app.error) {
      message.error(state.app.error);
      // 3秒后自动清除错误
      const timer = setTimeout(() => {
        dispatch({ type: ActionTypes.CLEAR_ERROR });
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [state.app.error]);
  
  // 通知处理
  useEffect(() => {
    state.app.notifications.forEach(notification => {
      if (!notification.shown) {
        switch (notification.type) {
          case 'success':
            message.success(notification.message);
            break;
          case 'warning':
            message.warning(notification.message);
            break;
          case 'error':
            message.error(notification.message);
            break;
          default:
            message.info(notification.message);
        }
        
        // 标记为已显示并在3秒后移除
        setTimeout(() => {
          dispatch({
            type: ActionTypes.REMOVE_NOTIFICATION,
            payload: notification.id
          });
        }, 3000);
      }
    });
  }, [state.app.notifications]);
  
  // Action creators
  const actions = {
    // 应用状态管理
    setLoading: (loading) => dispatch({ type: ActionTypes.SET_LOADING, payload: loading }),
    setError: (error) => dispatch({ type: ActionTypes.SET_ERROR, payload: error }),
    clearError: () => dispatch({ type: ActionTypes.CLEAR_ERROR }),
    setCurrentStep: (step) => dispatch({ type: ActionTypes.SET_CURRENT_STEP, payload: step }),
    
    // 通知管理
    addNotification: (message, type = 'info') => {
      const notification = {
        id: Date.now(),
        message,
        type,
        timestamp: new Date().toISOString(),
        shown: false
      };
      dispatch({ type: ActionTypes.ADD_NOTIFICATION, payload: notification });
    },
    
    // 项目管理
    setProject: (project) => dispatch({ type: ActionTypes.SET_PROJECT, payload: project }),
    updateProject: (updates) => dispatch({ type: ActionTypes.UPDATE_PROJECT, payload: updates }),
    setScript: (script) => dispatch({ type: ActionTypes.SET_SCRIPT, payload: script }),
    setVideoConfig: (config) => dispatch({ type: ActionTypes.SET_VIDEO_CONFIG, payload: config }),
    setVideoId: (videoId) => dispatch({ type: ActionTypes.SET_VIDEO_ID, payload: videoId }),
    markProjectDirty: () => dispatch({ type: ActionTypes.MARK_PROJECT_DIRTY }),
    markProjectClean: () => dispatch({ type: ActionTypes.MARK_PROJECT_CLEAN }),
    
    // 编辑器管理
    setActiveTab: (tab) => dispatch({ type: ActionTypes.SET_ACTIVE_TAB, payload: tab }),
    updateTimeline: (updates) => dispatch({ type: ActionTypes.UPDATE_TIMELINE, payload: updates }),
    updateTextStyle: (updates) => dispatch({ type: ActionTypes.UPDATE_TEXT_STYLE, payload: updates }),
    setAssets: (assets) => dispatch({ type: ActionTypes.SET_ASSETS, payload: assets }),
    addAsset: (asset) => dispatch({ type: ActionTypes.ADD_ASSET, payload: asset }),
    removeAsset: (assetId) => dispatch({ type: ActionTypes.REMOVE_ASSET, payload: assetId }),
    selectAssets: (assetIds) => dispatch({ type: ActionTypes.SELECT_ASSETS, payload: assetIds }),
    
    // 预览管理
    updatePreview: (updates) => dispatch({ type: ActionTypes.UPDATE_PREVIEW, payload: updates }),
    setPreviewStatus: (status) => dispatch({ type: ActionTypes.SET_PREVIEW_STATUS, payload: status }),
    setPreviewProgress: (progress) => dispatch({ type: ActionTypes.SET_PREVIEW_PROGRESS, payload: progress }),
    
    // 用户设置
    updateUserPreferences: (preferences) => dispatch({ type: ActionTypes.UPDATE_USER_PREFERENCES, payload: preferences })
  };
  
  return (
    <AppContext.Provider value={{ state, actions }}>
      {children}
    </AppContext.Provider>
  );
};

// 自定义 Hook
export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

// 便捷的 Hooks
export const useAppState = () => {
  const { state } = useAppContext();
  return state;
};

export const useAppActions = () => {
  const { actions } = useAppContext();
  return actions;
};

export const useProject = () => {
  const { state, actions } = useAppContext();
  return {
    project: state.project,
    setScript: actions.setScript,
    setVideoConfig: actions.setVideoConfig,
    setVideoId: actions.setVideoId,
    updateProject: actions.updateProject,
    markDirty: actions.markProjectDirty,
    markClean: actions.markProjectClean
  };
};

export const useEditor = () => {
  const { state, actions } = useAppContext();
  return {
    editor: state.editor,
    setActiveTab: actions.setActiveTab,
    updateTimeline: actions.updateTimeline,
    updateTextStyle: actions.updateTextStyle,
    assets: state.editor.assets,
    setAssets: actions.setAssets,
    addAsset: actions.addAsset,
    removeAsset: actions.removeAsset,
    selectedAssets: state.editor.selectedAssets,
    selectAssets: actions.selectAssets
  };
};

export const usePreview = () => {
  const { state, actions } = useAppContext();
  return {
    preview: state.preview,
    updatePreview: actions.updatePreview,
    setStatus: actions.setPreviewStatus,
    setProgress: actions.setPreviewProgress
  };
};

export default AppContext;