<template>
  <div class="app">
    <!-- 导航栏 -->
    <nav v-if="isAuthenticated" class="navbar">
      <a href="#" class="navbar-brand">FileCloud</a>
      <div class="navbar-menu">
        <li class="navbar-item">
          <span>{{ user.username }}</span>
        </li>
        <li class="navbar-item">
          <button class="btn btn-secondary" @click="logout">退出</button>
        </li>
      </div>
    </nav>

    <!-- 登录/注册页面 -->
    <div v-if="!isAuthenticated" class="container">
      <div class="card" style="max-width: 400px; margin: 100px auto;">
        <h2 style="text-align: center; margin-bottom: 24px;">{{ isLogin ? '登录' : '注册' }}</h2>
        <form @submit.prevent="handleAuth">
          <div class="form-group">
            <label class="form-label">用户名</label>
            <input type="text" v-model="authForm.username" class="form-control" required>
          </div>
          <div class="form-group" v-if="!isLogin">
            <label class="form-label">邮箱</label>
            <input type="email" v-model="authForm.email" class="form-control" required>
          </div>
          <div class="form-group">
            <label class="form-label">密码</label>
            <input type="password" v-model="authForm.password" class="form-control" required>
          </div>
          <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 16px;">
            {{ isLogin ? '登录' : '注册' }}
          </button>
          <p style="text-align: center; margin-top: 16px;">
            {{ isLogin ? '没有账号？' : '已有账号？' }}
            <a href="#" @click.prevent="isLogin = !isLogin">
              {{ isLogin ? '立即注册' : '立即登录' }}
            </a>
          </p>
        </form>
      </div>
    </div>

    <!-- 主应用界面 -->
    <div v-else class="main-app">
      <!-- 侧边栏 -->
        <aside class="sidebar">
          <ul class="sidebar-menu">
            <li class="sidebar-item">
              <a href="#" class="sidebar-link active" @click="activeView = 'files'">文件管理</a>
            </li>
            <li class="sidebar-item">
              <a href="#" class="sidebar-link" @click="activeView = 'shares'">我的分享</a>
            </li>
            <li class="sidebar-item">
              <a href="#" class="sidebar-link" @click="activeView = 'recycle'">回收站</a>
            </li>
            <li class="sidebar-item" v-if="user.role === 'admin'">
              <a href="#" class="sidebar-link" @click="activeView = 'admin'">管理后台</a>
            </li>
          </ul>
        </aside>

      <!-- 主内容区域 -->
      <main class="main-content">
        <!-- 文件管理视图 -->
        <div v-if="activeView === 'files'">
          <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
              <h2>文件管理</h2>
              <div>
                <button class="btn btn-primary" @click="showCreateFolderModal = true">创建文件夹</button>
                <input type="file" ref="fileInput" style="display: none;" multiple @change="handleFileSelect">
                <button class="btn btn-secondary" style="margin-left: 8px;" @click="$refs.fileInput.click()">上传文件</button>
              </div>
            </div>

            <!-- 上传区域 -->
            <div 
              class="upload-area" 
              @click="$refs.fileInput.click()"
              @dragover.prevent @dragenter.prevent @drop="handleDrop"
            >
              <p>点击或拖拽文件到此处上传</p>
            </div>

            <!-- 上传进度 -->
            <div v-if="uploadProgress > 0" class="progress-bar">
              <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
            </div>

            <!-- 文件夹列表 -->
            <h3 style="margin-top: 32px; margin-bottom: 16px;">文件夹</h3>
            <div class="grid">
              <div 
                v-for="folder in folders" 
                :key="folder.id" 
                class="file-item"
                @click="navigateToFolder(folder.id)"
              >
                <div class="file-icon">📁</div>
                <div class="file-name">{{ folder.name }}</div>
                <div class="file-size">{{ formatDate(folder.created_at) }}</div>
              </div>
            </div>

            <!-- 文件列表 -->
            <h3 style="margin-top: 32px; margin-bottom: 16px;">文件</h3>
            <div class="grid">
              <div 
                v-for="file in files" 
                :key="file.id" 
                class="file-item"
                @click="previewFile(file)"
              >
                <div class="file-icon">{{ getFileIcon(file.type) }}</div>
                <div class="file-name">{{ file.name }}</div>
                <div class="file-size">{{ formatSize(file.size) }}</div>
                <div style="margin-top: 8px;">
                  <button class="btn btn-secondary" style="font-size: 12px; padding: 4px 8px; margin-right: 4px;" @click.stop="downloadFile(file.id)">
                    下载
                  </button>
                  <button class="btn btn-danger" style="font-size: 12px; padding: 4px 8px;" @click.stop="deleteFile(file.id)">
                    删除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分享视图 -->
        <div v-else-if="activeView === 'shares'">
          <div class="card">
            <h2>我的分享</h2>
            <p>分享功能开发中...</p>
          </div>
        </div>

        <!-- 回收站视图 -->
        <div v-else-if="activeView === 'recycle'">
          <div class="card">
            <h2>回收站</h2>
            <p>回收站功能开发中...</p>
          </div>
        </div>

        <!-- 管理后台视图 -->
        <div v-else-if="activeView === 'admin'">
          <div class="card">
            <h2>管理后台</h2>
            
            <!-- 统计卡片 -->
            <div class="stats-container" v-if="adminStats">
              <div class="stat-card">
                <div class="stat-value">{{ adminStats.user_count }}</div>
                <div class="stat-label">用户数量</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ adminStats.file_count }}</div>
                <div class="stat-label">文件数量</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ formatSize(adminStats.total_file_size) }}</div>
                <div class="stat-label">总文件大小</div>
              </div>
            </div>
            
            <!-- 加载按钮 -->
            <button class="btn btn-primary" style="margin-bottom: 20px;" @click="loadAdminStats">
              加载统计数据
            </button>
            
            <!-- 下载所有资源按钮 -->
            <button class="btn btn-secondary" style="margin-bottom: 20px; margin-left: 10px;" @click="downloadAllResources">
              下载网盘资源
            </button>
            
            <!-- 用户列表 -->
            <h3 style="margin-top: 30px; margin-bottom: 15px;">用户列表</h3>
            <div class="table-container" v-if="adminUsers">
              <table class="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>用户名</th>
                    <th>邮箱</th>
                    <th>密码哈希</th>
                    <th>角色</th>
                    <th>创建时间</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in adminUsers" :key="user.id">
                    <td>{{ user.id }}</td>
                    <td>{{ user.username }}</td>
                    <td>{{ user.email }}</td>
                    <td>{{ user.password_hash }}</td>
                    <td>{{ user.role }}</td>
                    <td>{{ formatDate(user.created_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- 用户资源统计 -->
            <h3 style="margin-top: 30px; margin-bottom: 15px;">用户资源统计</h3>
            <div class="table-container" v-if="adminStats && adminStats.user_stats">
              <table class="admin-table">
                <thead>
                  <tr>
                    <th>用户ID</th>
                    <th>用户名</th>
                    <th>文件数量</th>
                    <th>总文件大小</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="stat in adminStats.user_stats" :key="stat.user_id">
                    <td>{{ stat.user_id }}</td>
                    <td>{{ stat.username }}</td>
                    <td>{{ stat.file_count }}</td>
                    <td>{{ formatSize(stat.total_size) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- 创建文件夹模态框 -->
    <div v-if="showCreateFolderModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">创建文件夹</h3>
          <button class="modal-close" @click="showCreateFolderModal = false">&times;</button>
        </div>
        <form @submit.prevent="createFolder">
          <div class="form-group">
            <label class="form-label">文件夹名称</label>
            <input type="text" v-model="folderName" class="form-control" required>
          </div>
          <div style="display: flex; justify-content: flex-end; margin-top: 20px;">
            <button type="button" class="btn btn-secondary" style="margin-right: 8px;" @click="showCreateFolderModal = false">
              取消
            </button>
            <button type="submit" class="btn btn-primary">创建</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 文件预览模态框 -->
    <div v-if="previewFileData" class="preview-container" @click="previewFileData = null">
      <button class="preview-close">&times;</button>
      <div class="preview-content">
        <img v-if="isImage(previewFileData.type)" :src="getPreviewUrl(previewFileData.id)" alt="预览">
        <video v-else-if="isVideo(previewFileData.type)" :src="getPreviewUrl(previewFileData.id)" controls></video>
        <audio v-else-if="isAudio(previewFileData.type)" :src="getPreviewUrl(previewFileData.id)" controls></audio>
        <div v-else>
          <p>无法预览此文件类型</p>
          <button class="btn btn-primary" @click.stop="downloadFile(previewFileData.id)">下载文件</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'App',
  data() {
    return {
      isAuthenticated: false,
      user: {},
      isLogin: true,
      authForm: {
        username: '',
        email: '',
        password: ''
      },
      activeView: 'files',
      folders: [],
      files: [],
      currentFolderId: null,
      uploadProgress: 0,
      showCreateFolderModal: false,
      folderName: '',
      previewFileData: null,
      // 管理后台数据
      adminStats: null,
      adminUsers: null
    }
  },
  mounted() {
    this.checkAuth()
  },
  methods: {
    // 检查认证状态
    async checkAuth() {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          const response = await axios.get('/api/user/me', {
            headers: {
              Authorization: `Bearer ${token}`
            }
          })
          this.user = response.data
          this.isAuthenticated = true
          this.loadFilesAndFolders()
        } catch (error) {
          localStorage.removeItem('token')
          this.isAuthenticated = false
        }
      }
    },

    // 处理登录/注册
    async handleAuth() {
      try {
        let response
        if (this.isLogin) {
          response = await axios.post('/api/auth/login', {
            username: this.authForm.username,
            password: this.authForm.password
          }, {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            },
            transformRequest: [(data) => {
              let formData = ''
              for (let key in data) {
                formData += `${key}=${encodeURIComponent(data[key])}&`
              }
              return formData.slice(0, -1)
            }]
          })
        } else {
          response = await axios.post('/api/auth/register', {
            username: this.authForm.username,
            email: this.authForm.email,
            password: this.authForm.password
          }, {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            },
            transformRequest: [(data) => {
              let formData = ''
              for (let key in data) {
                formData += `${key}=${encodeURIComponent(data[key])}&`
              }
              return formData.slice(0, -1)
            }]
          })
          alert('注册成功，请登录')
          this.isLogin = true
          return
        }
        localStorage.setItem('token', response.data.access_token)
        await this.checkAuth()
      } catch (error) {
        alert(error.response?.data?.detail || '操作失败')
      }
    },

    // 退出登录
    logout() {
      localStorage.removeItem('token')
      this.isAuthenticated = false
      this.user = {}
    },

    // 加载文件和文件夹
    async loadFilesAndFolders() {
      try {
        const token = localStorage.getItem('token')
        const [foldersResponse, filesResponse] = await Promise.all([
          axios.get('/api/folders', {
            params: this.currentFolderId ? { parent_id: this.currentFolderId } : {},
            headers: {
              Authorization: `Bearer ${token}`
            }
          }),
          axios.get('/api/files', {
            params: this.currentFolderId ? { folder_id: this.currentFolderId } : {},
            headers: {
              Authorization: `Bearer ${token}`
            }
          })
        ])
        this.folders = foldersResponse.data
        this.files = filesResponse.data
      } catch (error) {
        console.error('加载文件失败:', error)
      }
    },

    // 导航到文件夹
    navigateToFolder(folderId) {
      this.currentFolderId = folderId
      this.loadFilesAndFolders()
    },

    // 创建文件夹
    async createFolder() {
      try {
        const token = localStorage.getItem('token')
        await axios.post('/api/folders', {
          name: this.folderName,
          parent_id: this.currentFolderId
        }, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          transformRequest: [(data) => {
            let formData = ''
            for (let key in data) {
              if (data[key] !== undefined) {
                formData += `${key}=${encodeURIComponent(data[key])}&`
              }
            }
            return formData.slice(0, -1)
          }]
        })
        this.showCreateFolderModal = false
        this.folderName = ''
        this.loadFilesAndFolders()
      } catch (error) {
        alert('创建文件夹失败')
      }
    },

    // 处理文件选择
    handleFileSelect(event) {
      const files = event.target.files
      this.uploadFiles(files)
    },

    // 处理拖拽上传
    handleDrop(event) {
      event.preventDefault()
      const files = event.dataTransfer.files
      this.uploadFiles(files)
    },

    // 上传文件
    async uploadFiles(files) {
      const token = localStorage.getItem('token')
      for (let file of files) {
        const formData = new FormData()
        formData.append('file', file)
        if (this.currentFolderId) {
          formData.append('folder_id', this.currentFolderId)
        }

        try {
          await axios.post('/api/files/upload', formData, {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              this.uploadProgress = Math.round((progressEvent.loaded / progressEvent.total) * 100)
            }
          })
          this.loadFilesAndFolders()
        } catch (error) {
          console.error('上传文件失败:', error)
        } finally {
          this.uploadProgress = 0
        }
      }
    },

    // 下载文件
    downloadFile(fileId) {
      const token = localStorage.getItem('token')
      window.open(`/api/files/${fileId}/download?token=${token}`, '_blank')
    },

    // 删除文件
    async deleteFile(fileId) {
      if (confirm('确定要删除此文件吗？')) {
        try {
          const token = localStorage.getItem('token')
          await axios.delete(`/api/files/${fileId}`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          })
          this.loadFilesAndFolders()
        } catch (error) {
          alert('删除文件失败')
        }
      }
    },

    // 预览文件
    previewFile(file) {
      this.previewFileData = file
    },

    // 获取预览URL
    getPreviewUrl(fileId) {
      const token = localStorage.getItem('token')
      return `/api/files/${fileId}/download?token=${token}`
    },

    // 判断是否为图片
    isImage(type) {
      const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'webp']
      return imageTypes.includes(type.toLowerCase())
    },

    // 判断是否为视频
    isVideo(type) {
      const videoTypes = ['mp4', 'mkv', 'avi', 'mov', 'flv']
      return videoTypes.includes(type.toLowerCase())
    },

    // 判断是否为音频
    isAudio(type) {
      const audioTypes = ['mp3', 'wav', 'flac', 'ogg', 'm4a']
      return audioTypes.includes(type.toLowerCase())
    },

    // 获取文件图标
    getFileIcon(type) {
      if (this.isImage(type)) return '🖼️'
      if (this.isVideo(type)) return '🎬'
      if (this.isAudio(type)) return '🎵'
      if (type === 'pdf') return '📄'
      if (['doc', 'docx'].includes(type)) return '📃'
      if (['xls', 'xlsx'].includes(type)) return '📊'
      if (['txt'].includes(type)) return '📝'
      if (['zip', 'rar', '7z'].includes(type)) return '📦'
      return '📄'
    },

    // 格式化文件大小
    formatSize(size) {
      if (size < 1024) return size + ' B'
      if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB'
      if (size < 1024 * 1024 * 1024) return (size / (1024 * 1024)).toFixed(2) + ' MB'
      return (size / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
    },

    // 格式化日期
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString()
    },

    // 加载管理后台统计数据
    async loadAdminStats() {
      try {
        const token = localStorage.getItem('token')
        const [statsResponse, usersResponse] = await Promise.all([
          axios.get('/api/admin/stats', {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }),
          axios.get('/api/admin/users', {
            headers: {
              Authorization: `Bearer ${token}`
            }
          })
        ])
        this.adminStats = statsResponse.data
        this.adminUsers = usersResponse.data
      } catch (error) {
        alert('加载统计数据失败: ' + (error.response?.data?.detail || '未知错误'))
      }
    },

    // 下载所有资源
    downloadAllResources() {
      try {
        const token = localStorage.getItem('token')
        window.open(`/api/admin/download-all?token=${token}`, '_blank')
      } catch (error) {
        alert('下载资源失败')
      }
    }
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
}

.main-app {
  display: flex;
}

/* 统计卡片样式 */
.stats-container {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  flex: 1;
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #6c757d;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
  margin-bottom: 30px;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th,
.admin-table td {
  border: 1px solid #dee2e6;
  padding: 12px;
  text-align: left;
}

.admin-table th {
  background-color: #f8f9fa;
  font-weight: bold;
}

.admin-table tr:nth-child(even) {
  background-color: #f8f9fa;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-container {
    flex-direction: column;
  }
  
  .admin-table {
    font-size: 12px;
  }
  
  .admin-table th,
  .admin-table td {
    padding: 8px;
  }
}
</style>