<template>
  <div class="app">
    <div class="menu-bar">
      <!-- Update the menu items to use router-link -->
      <div class="menu-bar-left">
        <img src="../assets/LMlogo.png" alt="LMlogo">
        <router-link to="/home" active-class="active-link">LiU Marketplace</router-link>
        <router-link to="/buy" active-class="active-link">Köpa</router-link>
        <router-link to="/sell" active-class="active-link">Sälja</router-link>
      </div>
      <div class="menu-bar-right">
        <router-link to="/profile" active-class="active-link">Min Profil</router-link>
        <router-link to="/logout" active-class="active-link">Logga Ut</router-link>
      </div>
    </div>
    <!-- Add router-view to display the current page content -->
    <router-view></router-view>
  </div>
  <footer class="footer">
    <div class="column">
      <h3><strong>Mer info</strong></h3>
      <ul>
        <li><router-link to="/om-oss">Om oss</router-link></li>
        <li><router-link to="/vanliga-fragor">Vanliga Frågor</router-link></li>
        <li><router-link to="/kontakta-oss">Kontakta oss</router-link></li>
      </ul>
    </div>
    <div class="column">
      <h3><strong>LiU Marketplace</strong></h3>
      <p>For Students - By Students</p>
      <p class="copyright">© LiU Marketplace 2024</p>
    </div>
    <div class="column">
      <img src="../assets/LMlogo.png" alt="LMlogo">
    </div>
  </footer>
</template>

<script>
export default {
  name: 'HelloWorld',
  props: {
    msg: String,
    auth: {
      type: Boolean,
      required: true,
      default: true
    }
  },
}
</script>

<style scoped>

.active-link {
  font-weight: bold;
}

.app {
  font-family: Arial, sans-serif;
  padding-top: 80px;
}

.menu-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #0c264d; 
  color: white;
  padding: 10px 20px; 
  height: 80px;
}

.menu-bar-left {
  display: flex;
  align-items: center;

}

.menu-bar-right {
  display: flex;
}

.menu-bar a {
  color: white; /* White text color for menu items */
  text-decoration: none; /* Remove underline */
  margin-right: 20px; /* Add margin between menu items */
  font-family:'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
  font-size: 25px;
}

.menu-bar a:hover {
  text-decoration: underline; /* Add underline on hover */
}

.footer {
  display: flex;
  justify-content: center;
  background-color: #0c264d;
  height: 300px;
  padding: 60px;
  text-align: center;
}

.column {
  width: 30%;
}

.column ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

p {
  color: white;
}

h3 {
  color: white
}

.footer a {
  color: white; /* White text color for menu items */
  text-decoration: none; /* Remove underline */
}

.column img {
  max-width: 150px;
}

.menu-bar img {
  max-width: 50px;
  margin-right: 10px;
}

.copyright {
  font-size: 12px;
  margin-top: 100px;
}
</style>
