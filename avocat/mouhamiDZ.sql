-- Insert data into auth_user table
INSERT INTO auth_user (username, first_name, last_name, email, password)
VALUES
('john_doe', 'John', 'Doe', 'john.doe@example.com', 'hashed_password1'),
('jane_smith', 'Jane', 'Smith', 'jane.smith@example.com', 'hashed_password2'),
('lawfirm_admin', 'Law', 'Firm', 'admin@lawfirm.com', 'hashed_password3'),
('visitor_one', 'Visitor', 'One', 'visitor1@example.com', 'hashed_password4'),
('visitor_two', 'Visitor', 'Two', 'visitor2@example.com', 'hashed_password5');

-- Insert data into Langues table
INSERT INTO langues (langue) VALUES
('French'),
('English'),
('Spanish');

-- Insert data into Specialite table
INSERT INTO specialite (title, description) VALUES
('Criminal Law', 'Dealing with criminal offenses'),
('Family Law', 'Dealing with family-related issues'),
('Corporate Law', 'Dealing with business and corporate matters');

-- Insert data into Coordonnees table
INSERT INTO coordonnees (email) VALUES
('john.doe@example.com'),
('jane.smith@example.com'),
('contact@lawfirm.com');

-- Insert data into Avocat table
INSERT INTO avocat (user_id, firstName, lastName, adresse, coordonnees_id, dateWork, timeWork, evaluationStar) VALUES
(1, 'John', 'Doe', '123 Main St', 1, '2023-01-01', '08:00:00', 5),
(2, 'Jane', 'Smith', '456 Oak St', 2, '2023-01-02', '10:30:00', 4),
(3, 'Law', 'Firm', '789 Pine St', 3, '2023-01-03', '09:45:00', 4);

-- Insert data into Experience table
INSERT INTO experience (description, host_id) VALUES
('Worked in a prominent law firm', 1),
('Handled high-profile criminal cases', 3),
('Family law practice for over 10 years', 2);


-- Insert data into PhoneNumbers table
INSERT INTO phoneNumbers (phoneNumber, coordonnees_id) VALUES
('123-456-7890', 1),
('987-654-3210', 2),
('555-123-4567', 3);

-- Insert data into Post table
INSERT INTO posts (host_id, dateTimePub, title, content) VALUES
(1, '2023-01-01 12:00:00', 'Legal Updates', 'Recent changes in criminal law'),
(2, '2023-01-02 14:30:00', 'Family Law Insights', 'Navigating complex family legal matters'),
(3, '2023-01-03 11:15:00', 'Law Firm News', 'Expanding our legal services');

-- Insert data into Files table
INSERT INTO files (source) VALUES
('File 1 Source'),
('File 2 Source'),
('File 3 Source');

-- Insert data into Visitor table
INSERT INTO visitor (user_id, firstName, lastName) VALUES
(4, 'Andro', 'Biert'),
(5, 'Mohamed', 'Ouaddane');

-- Insert data into Comment table
INSERT INTO comment (host_id, avocat_id, dateTimePub, content) VALUES
(2, 1 , '2023-01-01 16:00:00', 'Great insights!'),
(1, 2 ,  '2023-01-02 18:45:00', 'Interesting perspective');

INSERT INTO avocat_specialite_price (avocat_id, specialite_id, price)
VALUES
  (1, 1, 50.00),
  (3, 3, 60.00),
  (2, 2, 55.00); 

  
INSERT INTO rendezvous (date_heure, statut, cause, avocat_id, utilisateur_id, title )
VALUES
    ('2023-01-01 10:00:00', 'Scheduled', 'Discuss case details', 1, 2, 'Meeting with Client A' ),
    ('2023-01-02 14:30:00', 'Completed', 'Review legal documents', 2, 2, 'Document Review'),
    ('2023-01-03 09:15:00', 'Pending', 'Provide legal advice', 3, 1, 'Legal Consultation');

-- Commit changes
COMMIT;
