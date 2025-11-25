import Cookies from 'js-cookie'

const TokenKey = 'Admin-Token'

export function getToken() {
  return Cookies.get(TokenKey)
}

export function setToken(token) {
    return Cookies.set(TokenKey, token, { expires: 7, path: import.meta.env.VITE_APP_BASE_URL })
}

export function removeToken() {
  return Cookies.remove(TokenKey)
}
