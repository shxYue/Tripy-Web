// 解析 JWT payload
function parseJwt(token) {
  try {
    const b64 = token.split('.')[1];
    const str = atob(b64.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(decodeURIComponent(escape(str)));
  } catch (e) {
    return {};
  }
}

// 更新顶栏的登录状态及管理员菜单可见性
function updateAuthState() {
  const token = localStorage.getItem("access_token");
  const adminToken = localStorage.getItem("admin_token");       // ← 新增
  const authBtn = document.getElementById("authBtn");
  if (authBtn) {
    if (adminToken || token) {
      authBtn.textContent = "退出";
      authBtn.href = "javascript:logout()";
    } else {
      authBtn.textContent = "登录";
      authBtn.href = "/static/pages/login.html";
    }
  }
  // 控制管理员链接显示
  const adminLink = document.getElementById("adminLink");
  if (adminLink) {
    adminLink.style.display = adminToken ? "block" : "none";    // ← 基于 admin_token
  }
}

// 通用脚本：加载 header.html 并绑定下拉交互
;(function(){
  const container = document.getElementById("headerContainer");
  if (!container) return;
  fetch("/static/header.html")
    .then(r => r.text())
    .then(html => {
      container.innerHTML = html;
      const dd = container.querySelector(".dropdown");
      const dc = container.querySelector(".dropdown-content");
      dd.addEventListener("mouseenter", () => dc.style.display = "block");
      dd.addEventListener("mouseleave", () => dc.style.display = "none");
      // 加载完毕后更新状态（包括管理员菜单可见性）
      updateAuthState();
    });
})();

// 动态引入 GSAP 动画库
(function() {
  if (!window.gsap) {
    const script = document.createElement('script');
    script.src = "https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js";
    script.onload = () => { window.gsapLoaded = true; };
    document.head.appendChild(script);
  }
})();

// 添加带认证的请求函数
function authFetch(url, options = {}) {
  const token = localStorage.getItem("access_token");
  const adminToken = localStorage.getItem("admin_token");       // ← 新增
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };
  // 管理员请求优先携带 X-Admin-Token
  if (adminToken) {
    headers["X-Admin-Token"] = adminToken;
  } else if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  
  return fetch(url, {
    ...options,
    headers
  }).then(res => {
    if (res.status === 401) {
      alert("请先登录！");
      window.location.href = "/static/pages/login.html";
      throw new Error("认证失败");
    }
    return res;
  });
}

// 退出登录
function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("admin_token");                       // ← 移除 admin_token
  alert("已退出登录");
  updateAuthState();
  window.location.href = "/static/pages/index.html";
}