import Cookies from 'js-cookie'

const TokenKey = 'Admin-Token'

export function getToken() {
    if (window.location.pathname.startsWith(import.meta.env.VITE_APP_BASE_URL)) {
        return Cookies.get(TokenKey)
    }
    return
}

export function setToken(token) {
    return Cookies.set(TokenKey, token, { expires: 7, path: import.meta.env.VITE_APP_BASE_URL })
}

export function removeToken() {
  return Cookies.remove(TokenKey, { path: import.meta.env.VITE_APP_BASE_URL })
}
