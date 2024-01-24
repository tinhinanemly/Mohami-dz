import React from 'react';


const Header = () => {
  return (
    <div className="header">
      <div className="logo-container">
        <span className="logo-text"> <h2>DZ-Mouhami</h2></span>
      </div>
      <div className="nav-links">
        <a href="#" className="nav-link">Home</a>
        <a href="#" className="nav-link">Annuaire</a>
        <a href="#" className="nav-link">Contact us</a>
        <a href="#" className="nav-link">Connexion</a>
        <a href="#" className="nav-link">Inscrire</a>
      </div>
    </div>
  );
};
export default Header;