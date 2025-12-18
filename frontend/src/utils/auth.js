import Cookies from 'js-cookie'

const TokenKey = 'Admin-Token' + import.meta.env.VITE_APP_BASE_URL.replace(/\//g, '-')

export function getToken() {
    return Cookies.get(TokenKey)
}

export function setToken(token) {
    // 如果已经有同名token，先删除
    if (getToken()) {
        removeToken()
    }
    return Cookies.set(TokenKey, token, { expires: 7, path: import.meta.env.VITE_APP_BASE_URL })
}

export function removeToken() {
  return Cookies.remove(TokenKey, { path: import.meta.env.VITE_APP_BASE_URL })
  return Cookies.remove(TokenKey, { path: import.meta.env.VITE_APP_BASE_URL })
}
