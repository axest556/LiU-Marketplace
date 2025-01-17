export function checkLoginStatus() {
  const token = sessionStorage.getItem('auth');
  let isLoggedIn = false;
  if (token) {
    const payload = JSON.parse(atob(token.split('.')[1]));
    console.log(payload);
    const expiryDate = new Date(payload.exp * 1000); // JWT exp is in seconds
    if (expiryDate > new Date()) {
      console.log('Token is valid');
      isLoggedIn = true;
    } else {
      isLoggedIn = false;
      sessionStorage.removeItem('auth');
    }
  } else {
    isLoggedIn = false;
  }
  return isLoggedIn;
}