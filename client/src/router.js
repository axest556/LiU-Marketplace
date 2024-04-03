import { createRouter, createWebHistory } from 'vue-router'; // Importera nödvändiga funktioner från vue-router

import HomePage from './components/HomePage.vue';
import BuyPage from './components/BuyPage.vue';
import SellPage from './components/SellPage.vue';
import ProfilePage from './components/ProfilePage.vue';
import LogoutPage from './components/LogoutPage.vue';
import AdsDetails from './components/AdsDetails.vue';
import NewAdPage from './components/NewAdPage.vue';
import FAQPage from './components/FAQPage.vue';
import ContactPage from './components/ContactPage.vue';
import AboutPage from './components/AboutPage.vue';
import LoginPage from './components/LoginPage.vue';
import HistoryPage from './components/HistoryPage.vue';
import EditProfilePage from './components/EditProfilePage.vue';

import LoginLayout from './layouts/login-layout.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage
  },
  {
    path: '/buy',
    name: 'buy',
    component: BuyPage
  },
  {
    path: '/sell',
    name: 'sell',
    component: SellPage
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfilePage
  },
  {
    path: '/logout',
    name: 'logout',
    component: LogoutPage
  },
  {
    path: '/ads/:id',
      name: 'AdsDetails',
      component: AdsDetails,
      props: route => ({
        id: parseInt(route.params.id),
        imageUrl: route.query.imageUrl,
        name: route.query.name,
        price: route.query.price,
        condition: route.query.condition,
        location: route.query.location,
        category: route.query.category,
        description: route.query.description
      })
  },
  {
    path: '/newad/:category',
    name: 'newad',
    component: NewAdPage,
    props: route => ({
      buttonText: route.query.buttonText
    })
  },
  {
    path: '/vanliga-fragor',
    name: 'faq',
    component: FAQPage
  },
  {
    path: '/kontakta-oss',
    name: 'contact',
    component: ContactPage
  },
  {
    path: '/om-oss',
    name: 'about',
    component: AboutPage
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { layout: LoginLayout}
  },
  {
    path: '/profile-history',
    name: 'history',
    component: HistoryPage
  },
  {
    path: '/edit-profile',
    name: 'editprofile',
    component: EditProfilePage
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return{ top: 0} ;
  }
});

export default router;
