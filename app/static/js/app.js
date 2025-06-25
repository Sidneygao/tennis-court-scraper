// 网球场地信息抓取系统 - 前端JavaScript

// 全局变量
let courtsData = [];
let filteredCourts = [];
let currentPage = 1;
const itemsPerPage = 12;

// 页面加载完成后执行
document.addEventListener("DOMContentLoaded", function () {
  console.log("网球场地信息抓取系统已加载");

  // 初始化应用
  initializeApp();

  // 绑定事件监听器
  bindEventListeners();

  loadCourtSearchSelector();
});

// 初始化应用
async function initializeApp() {
  try {
    // 并行加载数据
    await Promise.all([loadSystemStatus(), loadStats(), loadCourts()]);

    console.log("应用初始化完成");
  } catch (error) {
    console.error("应用初始化失败:", error);
    showNotification("应用初始化失败，请刷新页面重试", "error");
  }
}

// 绑定事件监听器
function bindEventListeners() {
  // 搜索功能
  const searchInput = document.getElementById("searchInput");
  if (searchInput) {
    searchInput.addEventListener("input", debounce(filterCourts, 300));
  }

  // 区域筛选
  const filterArea = document.getElementById("filterArea");
  if (filterArea) {
    filterArea.addEventListener("change", function () {
      loadCourts();
    });
  }
  const areaSelect = document.getElementById("areaSelect");
  if (areaSelect) {
    areaSelect.addEventListener("change", function () {
      loadCourts();
    });
  }

  // 分页功能
  document.addEventListener("click", function (e) {
    if (e.target.classList.contains("page-link")) {
      e.preventDefault();
      const page = parseInt(e.target.dataset.page);
      if (page) {
        currentPage = page;
        renderCourts();
      }
    }
  });
}

// 加载系统状态
async function loadSystemStatus() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) throw new Error("网络请求失败");

    const data = await response.json();
    updateSystemStatus(data);
  } catch (error) {
    console.error("加载系统状态失败:", error);
    updateSystemStatus({ status: "error", message: "无法获取系统状态" });
  }
}

// 更新系统状态显示
function updateSystemStatus(data) {
  const statusContainer = document.getElementById("systemStatus");
  if (!statusContainer) return;

  if (data.status === "healthy") {
    statusContainer.innerHTML = `
            <div class="row">
                <div class="col-6">
                    <div class="text-center">
                        <i class="fas fa-check-circle text-success fa-2x mb-2"></i>
                        <h6>系统状态</h6>
                        <small>正常运行</small>
                    </div>
                </div>
                <div class="col-6">
                    <div class="text-center">
                        <i class="fas fa-code-branch text-info fa-2x mb-2"></i>
                        <h6>版本</h6>
                        <small>v${data.version}</small>
                    </div>
                </div>
            </div>
        `;
  } else {
    statusContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${data.message || "系统状态异常"}
            </div>
        `;
  }
}

// 加载统计信息
async function loadStats() {
  try {
    const response = await fetch("/api/courts/stats/summary");
    if (!response.ok) throw new Error("网络请求失败");

    const data = await response.json();
    updateStatsDisplay(data);
  } catch (error) {
    console.error("加载统计信息失败:", error);
    showNotification("加载统计信息失败", "error");
  }
}

// 更新统计信息显示
function updateStatsDisplay(data) {
  const statsContainer = document.getElementById("statsContainer");
  if (!statsContainer) return;

  const statsHtml = `
        <div class="col-md-4 mb-4">
            <div class="card stats-card">
                <div class="card-body text-center">
                    <i class="fas fa-tennis-ball fa-3x mb-3"></i>
                    <h3>${data.total_courts}</h3>
                    <p class="mb-0">总场馆数</p>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-4">
            <div class="card stats-card">
                <div class="card-body text-center">
                    <i class="fas fa-map-marked-alt fa-3x mb-3"></i>
                    <h3>${Object.keys(data.area_stats).length}</h3>
                    <p class="mb-0">覆盖区域</p>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-4">
            <div class="card stats-card">
                <div class="card-body text-center">
                    <i class="fas fa-database fa-3x mb-3"></i>
                    <h3>${Object.keys(data.source_stats).length}</h3>
                    <p class="mb-0">数据源</p>
                </div>
            </div>
        </div>
    `;

  statsContainer.innerHTML = statsHtml;
}

// 加载场馆列表
async function loadCourts() {
  try {
    showLoading("courtsContainer", "正在加载场馆信息...");
    let area = "";
    const filterArea = document.getElementById("filterArea");
    if (filterArea) area = filterArea.value;
    if (!area) {
      const areaSelect = document.getElementById("areaSelect");
      if (areaSelect) area = areaSelect.value;
    }
    let url = "/api/courts?limit=1000";
    if (area) url += `&area=${encodeURIComponent(area)}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error("网络请求失败");
    courtsData = await response.json();

    // 为每个场馆加载详情数据以获取价格信息
    await loadCourtDetails();

    filteredCourts = [...courtsData];
    renderCourts();
  } catch (error) {
    console.error("加载场馆信息失败:", error);
    showError("courtsContainer", "加载场馆信息失败，请稍后重试");
  }
}

// 加载场馆详情数据
async function loadCourtDetails() {
  const promises = courtsData.map(async (court) => {
    try {
      const detailResponse = await fetch(`/api/details/${court.id}/preview`);
      if (detailResponse.ok) {
        const detailData = await detailResponse.json();
        if (detailData.has_detail && detailData.detail.merged_prices) {
          // 从详情数据中提取价格信息
          const prices = detailData.detail.merged_prices;

          // 分离真实价格和预测价格
          court.real_prices = [];
          court.predicted_prices = null;

          if (Array.isArray(prices)) {
            prices.forEach((price) => {
              if (price.type === "真实价格") {
                court.real_prices.push({
                  value: price.peak_price || price.off_peak_price,
                  unit: "元/小时",
                  type: "真实价格",
                  source: price.source || "bing_search",
                  notes: price.notes || [],
                  suspicious: price.suspicious || false,
                });
              } else if (price.type === "预测价格") {
                court.predicted_prices = {
                  max: price.peak_price,
                  mid: price.off_peak_price,
                  min: price.weekend_price,
                  unit: "元/小时",
                  confidence: price.confidence || 0.7,
                };
              }
            });
          }

          // 如果没有找到价格信息，使用场馆表的价格字段
          if (court.real_prices.length === 0 && !court.predicted_prices) {
            if (court.peak_price || court.off_peak_price) {
              court.real_prices.push({
                value: court.peak_price || court.off_peak_price,
                unit: "元/小时",
                type: "基础价格",
                source: "amap",
                notes: [],
                suspicious: false,
              });
            }
          }
        }
      }
    } catch (error) {
      console.error(`加载场馆 ${court.name} 详情失败:`, error);
    }
  });

  await Promise.all(promises);
}

// 渲染场馆列表
function renderCourts() {
  const container = document.getElementById("courtsContainer");
  if (!container) return;

  if (filteredCourts.length === 0) {
    container.innerHTML = `
            <div class="text-center">
                <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                <p>暂无场馆信息</p>
                <button class="btn btn-primary" onclick="scrapeData()">
                    <i class="fas fa-download me-1"></i>开始抓取数据
                </button>
            </div>
        `;
    return;
  }

  // 排序后分页
  const sortedCourts = sortCourtsForDisplay(filteredCourts);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const pageCourts = sortedCourts.slice(startIndex, endIndex);
  const courtsHtml = pageCourts.map((court) => createCourtCard(court)).join("");
  const paginationHtml = createPagination();

  container.innerHTML = courtsHtml + paginationHtml;
}

// 创建场馆卡片
function createCourtCard(court) {
  return `
        <div class="col-md-6 col-lg-4 mb-4 fade-in-up">
            <div class="card court-card h-100">
                <div class="card-body">
                    <h5 class="card-title mb-2">${escapeHtml(court.name)}</h5>
                    <p class="card-text text-muted">
                        <i class="fas fa-map-marker-alt me-1"></i>
                        ${escapeHtml(court.address)}
                    </p>
                    ${court.phone ? `<p class="card-text"><i class="fas fa-phone me-1"></i>${escapeHtml(court.phone)}</p>` : ""}
                    <p class="card-text text-muted">
                        <i class="fas fa-tools me-1"></i>
                        ${!court.facilities || court.facilities === "该数据不能获得" ? '<span class="text-muted">暂无设施信息</span>' : escapeHtml(court.facilities)}
                    </p>
                    ${createPriceInfoV2(court)}
                </div>
                <div class="card-footer bg-transparent">
                    <div class="d-flex justify-content-end align-items-center">
                        <button class="btn btn-sm btn-outline-primary" onclick="viewCourtDetail(${court.id})">
                            <i class="fas fa-eye me-1"></i>详情
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 新版价格信息渲染
function createPriceInfoV2(court) {
  // 优先显示真实价格
  if (court.real_prices && court.real_prices.length > 0) {
    let html = '<div class="price-info">';
    court.real_prices.forEach((p) => {
      let priceText = p.value ? `${p.value}${p.unit || ""}` : "价格待定";
      if (p.suspicious) {
        priceText += '<span class="text-danger ms-1">?</span>';
      }
      const sourceText =
        p.source === "bing_search"
          ? "Bing搜索"
          : p.source === "amap"
            ? "高德地图"
            : p.source;
      const typeBadge = p.type === "真实价格" ? "bg-success" : "bg-primary";
      html += `<div class="mb-1${p.suspicious ? " text-danger" : ""}">
                <span class="fw-bold">${escapeHtml(priceText)}</span> 
                <span class="badge ${typeBadge} ms-1">${escapeHtml(p.type)}</span> 
                <span class="badge bg-info ms-1">${escapeHtml(sourceText)}</span>
            </div>`;
      // 显示价格备注
      if (p.notes && p.notes.length > 0) {
        p.notes.forEach((note) => {
          html += `<small class="text-muted d-block">• ${escapeHtml(note)}</small>`;
        });
      }
    });
    html += "</div>";
    return html;
  }
  // 支持 predicted_prices 为数组格式
  if (
    Array.isArray(court.predicted_prices) &&
    court.predicted_prices.length > 0
  ) {
    let html = '<div class="price-info">';
    court.predicted_prices.forEach((p) => {
      html += `<div class="mb-1">
                <span class="fw-bold">${escapeHtml(p.value)}${p.unit || ""}</span> 
                <span class="badge bg-warning ms-1">${escapeHtml(p.type_label || p.type || "预测价格")}</span>
                <span class="badge bg-info ms-1">${escapeHtml(p.source || "价格预测")}</span>
            </div>`;
    });
    html += '<small class="text-muted">基于同类型场馆模型预测</small>';
    html += "</div>";
    return html;
  }
  // 兼容对象格式
  if (court.predicted_prices && typeof court.predicted_prices === "object") {
    let html = '<div class="price-info">';
    if (court.predicted_prices.max) {
      html += `<div class="mb-1">
                <span class="fw-bold">${escapeHtml(court.predicted_prices.max)}${court.predicted_prices.unit || ""}</span> 
                <span class="badge bg-warning ms-1">预测最高</span>
            </div>`;
    }
    if (court.predicted_prices.mid) {
      html += `<div class="mb-1">
                <span class="fw-bold">${escapeHtml(court.predicted_prices.mid)}${court.predicted_prices.unit || ""}</span> 
                <span class="badge bg-warning ms-1">预测中点</span>
            </div>`;
    }
    if (court.predicted_prices.min) {
      html += `<div class="mb-1">
                <span class="fw-bold">${escapeHtml(court.predicted_prices.min)}${court.predicted_prices.unit || ""}</span> 
                <span class="badge bg-warning ms-1">预测最低</span>
            </div>`;
    }
    html += '<small class="text-muted">基于同类型场馆模型预测</small>';
    html += "</div>";
    return html;
  }
  // 如果都没有，显示无价格信息
  return '<div class="text-muted"><small>价格信息待补充</small></div>';
}

// 创建分页
function createPagination() {
  const totalPages = Math.ceil(filteredCourts.length / itemsPerPage);
  if (totalPages <= 1) return "";

  let paginationHtml =
    '<div class="col-12 mt-4"><nav><ul class="pagination justify-content-center">';

  // 上一页
  if (currentPage > 1) {
    paginationHtml += `<li class="page-item"><a class="page-link" href="#" data-page="${currentPage - 1}">上一页</a></li>`;
  }

  // 页码
  for (let i = 1; i <= totalPages; i++) {
    if (i === currentPage) {
      paginationHtml += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
    } else {
      paginationHtml += `<li class="page-item"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
    }
  }

  // 下一页
  if (currentPage < totalPages) {
    paginationHtml += `<li class="page-item"><a class="page-link" href="#" data-page="${currentPage + 1}">下一页</a></li>`;
  }

  paginationHtml += "</ul></nav></div>";
  return paginationHtml;
}

// 筛选场馆
function filterCourts() {
  const searchTerm =
    document.getElementById("searchInput")?.value.toLowerCase() || "";
  const selectedArea = document.getElementById("filterArea")?.value || "";

  filteredCourts = courtsData.filter((court) => {
    const matchesSearch =
      court.name.toLowerCase().includes(searchTerm) ||
      court.address.toLowerCase().includes(searchTerm);
    const matchesArea = !selectedArea || court.area === selectedArea;
    return matchesSearch && matchesArea;
  });

  currentPage = 1; // 重置到第一页
  renderCourts();
}

// 抓取数据
async function scrapeData() {
  const area = document.getElementById("areaSelect")?.value || "";
  const button = event?.target;

  if (button) {
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>抓取中...';

    try {
      const url = area
        ? `/api/scraper/scrape/amap?area=${area}`
        : "/api/scraper/scrape/amap";
      const response = await fetch(url, { method: "POST" });

      if (!response.ok) throw new Error("网络请求失败");

      const data = await response.json();
      showNotification(data.message, "success");

      // 重新加载数据
      await Promise.all([loadStats(), loadCourts()]);
    } catch (error) {
      console.error("抓取数据失败:", error);
      showNotification("抓取数据失败: " + error.message, "error");
    } finally {
      if (button) {
        button.disabled = false;
        button.innerHTML = originalText;
      }
    }
  }
}

// 获取统计信息
async function getStats() {
  await loadStats();
  showNotification("统计信息已更新", "success");
}

// 清空数据
async function clearData() {
  if (!confirm("确定要清空所有数据吗？此操作不可恢复！")) {
    return;
  }

  try {
    const response = await fetch("/api/scraper/clear", { method: "DELETE" });

    if (!response.ok) throw new Error("网络请求失败");

    const data = await response.json();
    showNotification(data.message, "success");

    // 重新加载数据
    await Promise.all([loadStats(), loadCourts()]);
  } catch (error) {
    console.error("清空数据失败:", error);
    showNotification("清空数据失败: " + error.message, "error");
  }
}

// 查看场馆详情
async function viewCourtDetail(courtId) {
  try {
    showNotification("正在加载详情...", "info");

    // 获取详情数据
    const response = await fetch(`/api/details/${courtId}/preview`);
    if (!response.ok) throw new Error("网络请求失败");

    const data = await response.json();

    if (!data.has_detail) {
      // 没有详情数据，显示更新按钮
      showDetailModal(courtId, data.court_name, null);
    } else {
      // 显示详情数据
      showDetailModal(courtId, data.court_name, data.detail);
    }
  } catch (error) {
    console.error("获取详情失败:", error);
    showNotification("获取详情失败: " + error.message, "error");
  }
}

// 显示详情模态框
function showDetailModal(courtId, courtName, detailData) {
  // 创建模态框HTML
  let modalHtml = `
        <div class="modal fade" id="detailModal" tabindex="-1" aria-labelledby="detailModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="detailModalLabel">${escapeHtml(courtName)} - 详情</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" id="detailModalBody">
    `;

  if (detailData) {
    // 有详情数据
    modalHtml += `
            <div class="row">
                <div class="col-md-8">
                    <h6><i class="fas fa-info-circle me-2"></i>场馆介绍</h6>
                    <p class="text-muted">
                        ${escapeHtml(detailData.description && detailData.description !== "该数据不能获得" ? detailData.description : "暂无介绍")}
                    </p>
                    
                    <h6><i class="fas fa-star me-2"></i>综合评分</h6>
                    <div class="mb-3">
                        ${
                          detailData.rating && detailData.rating > 0
                            ? `<span class="badge bg-warning text-dark fs-6">${detailData.rating.toFixed(1)} 分</span>`
                            : '<span class="text-muted small">暂无评分</span>'
                        }
                    </div>
                    
                    <h6><i class="fas fa-clock me-2"></i>营业时间</h6>
                    <p class="text-muted">
                        ${escapeHtml(detailData.business_hours && detailData.business_hours !== "该数据不能获得" ? detailData.business_hours : "暂无营业时间信息")}
                    </p>
                    
                    <h6><i class="fas fa-tools me-2"></i>设施服务</h6>
                    <p class="text-muted">
                        ${escapeHtml(detailData.facilities && detailData.facilities !== "该数据不能获得" ? detailData.facilities : "暂无设施信息")}
                    </p>
                </div>
                <div class="col-md-4">
                    <h6><i class="fas fa-comments me-2"></i>用户评论</h6>
                    <div class="mb-3">
                        ${
                          detailData.reviews && detailData.reviews.length > 0
                            ? (() => {
                                // 过滤掉虚拟评论
                                const realReviews = detailData.reviews.filter(review => 
                                  review.content && 
                                  review.content !== "该数据不能获得" && 
                                  !review.content.startsWith("该数据不能获得")
                                );
                                
                                if (realReviews.length > 0) {
                                  return realReviews
                                    .map(
                                      (review) => `
                                <div class="card mb-2">
                                    <div class="card-body p-2">
                                        <div class="d-flex justify-content-between align-items-start">
                                            <div class="flex-grow-1">
                                                <p class="mb-1 small">${escapeHtml(review.content || "")}</p>
                                                <small class="text-muted">${escapeHtml(review.user || "匿名用户")} - ${escapeHtml(review.date || "")}</small>
                                            </div>
                                            ${review.rating ? `<span class="badge bg-warning text-dark ms-2">${review.rating}分</span>` : ""}
                                        </div>
                                    </div>
                                </div>
                              `,
                                    )
                                    .join("");
                                } else {
                                  return '<p class="text-muted small">暂无用户评论</p>';
                                }
                              })()
                            : '<p class="text-muted small">暂无用户评论</p>'
                        }
                    </div>
                </div>
            </div>
            
            <div class="text-center mt-3">
                <small class="text-muted">
                    <i class="fas fa-clock me-1"></i>
                    最后更新: ${detailData.last_update ? new Date(detailData.last_update).toLocaleString() : "未知"}
                </small>
            </div>
        `;
  } else {
    // 没有详情数据
    modalHtml += `
            <div class="text-center py-5">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h6>暂无详情数据</h6>
                <p class="text-muted">点击下方按钮从大众点评和美团获取详细信息</p>
                <button class="btn btn-primary" onclick="updateCourtDetail(${courtId})">
                    <i class="fas fa-sync-alt me-1"></i>获取详情
                </button>
            </div>
        `;
  }

  modalHtml += `
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        ${
                          detailData
                            ? `<button type="button" class="btn btn-primary" onclick="updateCourtDetail(${courtId})">
                            <i class="fas fa-sync-alt me-1"></i>更新详情
                        </button>`
                            : ""
                        }
                    </div>
                </div>
            </div>
        </div>
    `;

  // 移除已存在的模态框
  const existingModal = document.getElementById("detailModal");
  if (existingModal) {
    existingModal.remove();
  }

  // 添加新模态框到页面
  document.body.insertAdjacentHTML("beforeend", modalHtml);

  // 显示模态框
  const modal = new bootstrap.Modal(document.getElementById("detailModal"));
  modal.show();
}

// 更新场馆详情
async function updateCourtDetail(courtId) {
  try {
    // 更新按钮状态
    const updateBtn = event.target;
    const originalText = updateBtn.innerHTML;
    updateBtn.disabled = true;
    updateBtn.innerHTML =
      '<i class="fas fa-spinner fa-spin me-1"></i>更新中...';

    // 调用更新API
    const response = await fetch(`/api/details/${courtId}/update`, {
      method: "POST",
    });
    if (!response.ok) throw new Error("网络请求失败");

    const data = await response.json();
    showNotification(data.message, "success");

    // 重新获取详情并更新模态框
    const detailResponse = await fetch(`/api/details/${courtId}/preview`);
    if (detailResponse.ok) {
      const detailData = await detailResponse.json();
      if (detailData.has_detail) {
        // 更新模态框内容
        const modalBody = document.getElementById("detailModalBody");
        if (modalBody) {
          // 重新显示模态框
          bootstrap.Modal.getInstance(
            document.getElementById("detailModal"),
          ).hide();
          setTimeout(() => {
            showDetailModal(courtId, detailData.court_name, detailData.detail);
          }, 300);
        }
      }
    }
  } catch (error) {
    console.error("更新详情失败:", error);
    showNotification("更新详情失败: " + error.message, "error");
  } finally {
    // 恢复按钮状态
    if (updateBtn) {
      updateBtn.disabled = false;
      updateBtn.innerHTML = originalText;
    }
  }
}

// 工具函数

// 防抖函数
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// HTML转义
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// 显示加载状态
function showLoading(containerId, message = "加载中...") {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
                <p class="mt-2">${message}</p>
            </div>
        `;
  }
}

// 显示错误信息
function showError(containerId, message) {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
  }
}

// 显示通知
function showNotification(message, type = "info") {
  // 创建通知元素
  const notification = document.createElement("div");
  notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  notification.style.cssText =
    "top: 20px; right: 20px; z-index: 9999; min-width: 300px;";
  notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  // 添加到页面
  document.body.appendChild(notification);

  // 自动移除
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 5000);
}

// 导出函数供全局使用
window.scrapeData = scrapeData;
window.getStats = getStats;
window.clearData = clearData;
window.viewCourtDetail = viewCourtDetail;

function sortCourtsForDisplay(courts) {
  // 只保留数字部分，便于比较
  function parsePrice(price) {
    if (!price) return null;
    // 提取第一个数字（支持"80元/小时"或"80/小时"）
    const match = price.match(/\d+(\.\d+)?/);
    return match ? parseFloat(match[0]) : null;
  }
  return courts.slice().sort((a, b) => {
    const aHasPrice = !!a.off_peak_price;
    const bHasPrice = !!b.off_peak_price;
    if (aHasPrice && bHasPrice) {
      const aPrice = parsePrice(a.off_peak_price);
      const bPrice = parsePrice(b.off_peak_price);
      if (aPrice != null && bPrice != null) {
        return aPrice - bPrice;
      } else if (aPrice != null) {
        return -1;
      } else if (bPrice != null) {
        return 1;
      } else {
        return 0;
      }
    } else if (aHasPrice) {
      return -1;
    } else if (bHasPrice) {
      return 1;
    } else {
      return 0;
    }
  });
}

// 新增：加载场馆搜索URL并渲染选择器
async function loadCourtSearchSelector() {
  const container = document.getElementById("courtSearchSelector");
  if (!container) return;
  try {
    const resp = await fetch("/api/courts/search_urls");
    if (!resp.ok) throw new Error("网络请求失败");
    const courts = await resp.json();
    let html = `<select id="courtSelect" class="form-select mb-2"><option value="">选择场馆...</option>`;
    for (const c of courts) {
      html += `<option value="${c.name}" data-dianping="${c.dianping_url}" data-meituan="${c.meituan_url}">${c.name}</option>`;
    }
    html += `</select>`;
    html += `<button id="gotoDianping" class="btn btn-sm btn-primary me-2">大众点评</button>`;
    html += `<button id="gotoMeituan" class="btn btn-sm btn-success">美团</button>`;
    container.innerHTML = html;
    document.getElementById("gotoDianping").onclick = function () {
      const sel = document.getElementById("courtSelect");
      const url = sel.options[sel.selectedIndex].getAttribute("data-dianping");
      if (url) window.open(url, "_blank");
    };
    document.getElementById("gotoMeituan").onclick = function () {
      const sel = document.getElementById("courtSelect");
      const url = sel.options[sel.selectedIndex].getAttribute("data-meituan");
      if (url) window.open(url, "_blank");
    };
  } catch (e) {
    container.innerHTML = '<div class="text-danger">加载场馆选择失败</div>';
  }
}
