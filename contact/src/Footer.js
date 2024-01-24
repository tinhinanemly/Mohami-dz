import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPhone } from '@fortawesome/free-solid-svg-icons';
import { faFacebookF, faTwitter, faInstagram } from '@fortawesome/free-brands-svg-icons';

const Footer = () => {
  const footerStyle = {
    
    bottom: 0,
    left: 0,
    display: 'flex',
    justifyContent: 'space-around',
    backgroundColor: '#000000',
    color: '#fff',
    padding: '40px',
    zIndex: 1000,
  };

  const columnStyle = {
    flex: '1',
    margin: '0 40px',
  };

  const linkStyle = {
    color: '#fff',
    textDecoration: 'none', // Remove the underline from the links
    marginBottom: '30px',
  };
  const whriteStyle = {
    color: '#CA965C', // Set the color of "Contact Us"
  };

  const socialIconStyle = {
    fontSize: '30px',
    margin: '0 10px',
    color: '#CA965C',
    
  };

  return (
    <footer style={footerStyle}>
      <div style={columnStyle}>
        <h3 style={whriteStyle}>About Us</h3>
        <p>
       our dedicated team of experienced attorneys is committed to providing personalized and effective legal solutions. We prioritize integrity, excellence, and client satisfaction in adressing a wide range of local issues . our passion for justice and advocacy sets us apart , making us not just legal practitioners but advocates for our client's peace of mind and succes within the legal system
        </p>
      </div>

      <div style={columnStyle}>
        <h3 style={whriteStyle}>Helpful Links</h3>
        <ul>
          <li><a href="#" style={linkStyle}>Home</a></li>
          <li><a href="#" style={linkStyle}>Annuaire</a></li>
          <li><a href="#" style={linkStyle}>Contact us</a></li>
          <li><a href="#" style={linkStyle}>Connexion</a></li>
          <li><a href="#" style={linkStyle}>Inscrire</a></li>
        </ul>
      </div>

      <div style={columnStyle}>
        <h3 style={whriteStyle}>contact us</h3>
        <p>
          <FontAwesomeIcon icon={faPhone} style={{ marginRight: '10px' }} />
          +213 697585418
        </p>
        <div className="social-icons">
          <a href='#'><FontAwesomeIcon icon={faFacebookF} style={socialIconStyle} /></a>
          <a href='#'><FontAwesomeIcon icon={faTwitter} style={socialIconStyle} /></a>
          <a href='#'><FontAwesomeIcon icon={faInstagram} style={socialIconStyle} /></a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;