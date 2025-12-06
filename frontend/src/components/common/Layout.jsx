import React from 'react';
import Header from './Header';
import Navigation from './Navigation';
import LoginPopup from '../auth/LoginPopup';
import '../../styles/common.css';

const Layout = ({ children }) => {
  return (
    <>
      <Header />
      <Navigation />
      {children}
      <LoginPopup />
    </>
  );
};

export default Layout;