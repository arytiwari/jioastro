-- Migration: Add Indian Cities with Coordinates
-- This migration creates the cities table and populates it with major Indian cities and towns
-- across all states and union territories with accurate latitude/longitude coordinates

-- Create cities table
CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    display_name VARCHAR(200) NOT NULL
);

-- Create indexes for better search performance
CREATE INDEX IF NOT EXISTS idx_cities_name ON cities(name);
CREATE INDEX IF NOT EXISTS idx_cities_state ON cities(state);
CREATE INDEX IF NOT EXISTS idx_cities_display_name ON cities(display_name);

-- Truncate table if it exists (for clean re-import)
TRUNCATE TABLE cities RESTART IDENTITY CASCADE;

-- Insert cities data
-- Format: (name, state, latitude, longitude, display_name)

-- ANDHRA PRADESH
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Visakhapatnam', 'Andhra Pradesh', 17.686815, 83.218482, 'Visakhapatnam, Andhra Pradesh'),
('Vijayawada', 'Andhra Pradesh', 16.506174, 80.648018, 'Vijayawada, Andhra Pradesh'),
('Guntur', 'Andhra Pradesh', 16.306919, 80.436631, 'Guntur, Andhra Pradesh'),
('Nellore', 'Andhra Pradesh', 14.433651, 79.986633, 'Nellore, Andhra Pradesh'),
('Kurnool', 'Andhra Pradesh', 15.828126, 78.037279, 'Kurnool, Andhra Pradesh'),
('Rajahmundry', 'Andhra Pradesh', 17.005171, 81.797720, 'Rajahmundry, Andhra Pradesh'),
('Kakinada', 'Andhra Pradesh', 16.960220, 82.247668, 'Kakinada, Andhra Pradesh'),
('Tirupati', 'Andhra Pradesh', 13.635540, 79.419745, 'Tirupati, Andhra Pradesh'),
('Anantapur', 'Andhra Pradesh', 14.678979, 77.603729, 'Anantapur, Andhra Pradesh'),
('Kadapa', 'Andhra Pradesh', 14.467090, 78.823860, 'Kadapa, Andhra Pradesh'),
('Vizianagaram', 'Andhra Pradesh', 18.111675, 83.393875, 'Vizianagaram, Andhra Pradesh'),
('Eluru', 'Andhra Pradesh', 16.712570, 81.104670, 'Eluru, Andhra Pradesh'),
('Ongole', 'Andhra Pradesh', 15.503565, 80.044671, 'Ongole, Andhra Pradesh'),
('Nandyal', 'Andhra Pradesh', 15.477804, 78.483582, 'Nandyal, Andhra Pradesh'),
('Machilipatnam', 'Andhra Pradesh', 16.187454, 81.138394, 'Machilipatnam, Andhra Pradesh'),
('Adoni', 'Andhra Pradesh', 15.627695, 77.274800, 'Adoni, Andhra Pradesh'),
('Tenali', 'Andhra Pradesh', 16.239847, 80.644264, 'Tenali, Andhra Pradesh'),
('Chittoor', 'Andhra Pradesh', 13.217096, 79.101540, 'Chittoor, Andhra Pradesh'),
('Hindupur', 'Andhra Pradesh', 13.828069, 77.491127, 'Hindupur, Andhra Pradesh'),
('Proddatur', 'Andhra Pradesh', 14.750206, 78.548271, 'Proddatur, Andhra Pradesh'),
('Bhimavaram', 'Andhra Pradesh', 16.544602, 81.521187, 'Bhimavaram, Andhra Pradesh'),
('Madanapalle', 'Andhra Pradesh', 13.550547, 78.502811, 'Madanapalle, Andhra Pradesh'),
('Guntakal', 'Andhra Pradesh', 15.166749, 77.377506, 'Guntakal, Andhra Pradesh'),
('Dharmavaram', 'Andhra Pradesh', 14.414284, 77.724633, 'Dharmavaram, Andhra Pradesh'),
('Gudivada', 'Andhra Pradesh', 16.433653, 80.996055, 'Gudivada, Andhra Pradesh'),
('Srikakulam', 'Andhra Pradesh', 18.298846, 83.896570, 'Srikakulam, Andhra Pradesh'),
('Narasaraopet', 'Andhra Pradesh', 16.234818, 80.049084, 'Narasaraopet, Andhra Pradesh'),
('Rajampet', 'Andhra Pradesh', 14.196074, 79.150894, 'Rajampet, Andhra Pradesh'),
('Tadpatri', 'Andhra Pradesh', 14.906886, 78.009529, 'Tadpatri, Andhra Pradesh'),
('Tadepalligudem', 'Andhra Pradesh', 16.815014, 81.527481, 'Tadepalligudem, Andhra Pradesh'),
('Chilakaluripet', 'Andhra Pradesh', 16.089165, 80.167030, 'Chilakaluripet, Andhra Pradesh'),
('Yemmiganur', 'Andhra Pradesh', 15.729421, 77.479622, 'Yemmiganur, Andhra Pradesh'),
('Kavali', 'Andhra Pradesh', 14.913609, 79.995003, 'Kavali, Andhra Pradesh'),
('Palacole', 'Andhra Pradesh', 16.520004, 81.777916, 'Palacole, Andhra Pradesh'),
('Vinukonda', 'Andhra Pradesh', 16.052696, 79.739036, 'Vinukonda, Andhra Pradesh');

-- ARUNACHAL PRADESH
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Itanagar', 'Arunachal Pradesh', 27.102214, 93.691790, 'Itanagar, Arunachal Pradesh'),
('Naharlagun', 'Arunachal Pradesh', 27.104099, 93.698784, 'Naharlagun, Arunachal Pradesh'),
('Pasighat', 'Arunachal Pradesh', 28.066667, 95.326667, 'Pasighat, Arunachal Pradesh'),
('Tawang', 'Arunachal Pradesh', 27.586278, 91.861404, 'Tawang, Arunachal Pradesh'),
('Ziro', 'Arunachal Pradesh', 27.544761, 93.831552, 'Ziro, Arunachal Pradesh'),
('Bomdila', 'Arunachal Pradesh', 27.264163, 92.418343, 'Bomdila, Arunachal Pradesh'),
('Tezu', 'Arunachal Pradesh', 27.917175, 96.168274, 'Tezu, Arunachal Pradesh'),
('Seppa', 'Arunachal Pradesh', 27.279936, 92.801979, 'Seppa, Arunachal Pradesh'),
('Along', 'Arunachal Pradesh', 28.175206, 94.801025, 'Along, Arunachal Pradesh'),
('Changlang', 'Arunachal Pradesh', 27.136902, 95.722404, 'Changlang, Arunachal Pradesh');

-- ASSAM
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Guwahati', 'Assam', 26.144518, 91.736238, 'Guwahati, Assam'),
('Silchar', 'Assam', 24.827225, 92.798293, 'Silchar, Assam'),
('Dibrugarh', 'Assam', 27.479427, 94.908723, 'Dibrugarh, Assam'),
('Jorhat', 'Assam', 26.756767, 94.216929, 'Jorhat, Assam'),
('Nagaon', 'Assam', 26.348026, 92.681635, 'Nagaon, Assam'),
('Tinsukia', 'Assam', 27.488857, 95.364548, 'Tinsukia, Assam'),
('Tezpur', 'Assam', 26.633333, 92.800000, 'Tezpur, Assam'),
('Bongaigaon', 'Assam', 26.481361, 90.557823, 'Bongaigaon, Assam'),
('Dhubri', 'Assam', 26.019815, 89.986427, 'Dhubri, Assam'),
('Barpeta', 'Assam', 26.323151, 91.005554, 'Barpeta, Assam'),
('Goalpara', 'Assam', 26.172691, 90.615782, 'Goalpara, Assam'),
('Karimganj', 'Assam', 24.867945, 92.348175, 'Karimganj, Assam'),
('Sibsagar', 'Assam', 26.984518, 94.637772, 'Sibsagar, Assam'),
('Golaghat', 'Assam', 26.517619, 93.957520, 'Golaghat, Assam'),
('Diphu', 'Assam', 25.843515, 93.432190, 'Diphu, Assam'),
('North Lakhimpur', 'Assam', 27.234627, 94.104507, 'North Lakhimpur, Assam'),
('Mangaldoi', 'Assam', 26.444063, 92.031006, 'Mangaldoi, Assam'),
('Haflong', 'Assam', 25.172047, 93.015968, 'Haflong, Assam'),
('Hojai', 'Assam', 26.001125, 92.854797, 'Hojai, Assam'),
('Kokrajhar', 'Assam', 26.400849, 90.271812, 'Kokrajhar, Assam');

-- BIHAR
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Patna', 'Bihar', 25.594095, 85.137566, 'Patna, Bihar'),
('Gaya', 'Bihar', 24.795802, 84.997503, 'Gaya, Bihar'),
('Bhagalpur', 'Bihar', 25.244583, 86.983334, 'Bhagalpur, Bihar'),
('Muzaffarpur', 'Bihar', 26.120000, 85.390000, 'Muzaffarpur, Bihar'),
('Darbhanga', 'Bihar', 26.152460, 85.897392, 'Darbhanga, Bihar'),
('Purnia', 'Bihar', 25.778816, 87.475028, 'Purnia, Bihar'),
('Arrah', 'Bihar', 25.556418, 84.662826, 'Arrah, Bihar'),
('Begusarai', 'Bihar', 25.418466, 86.133879, 'Begusarai, Bihar'),
('Katihar', 'Bihar', 25.539469, 87.577448, 'Katihar, Bihar'),
('Munger', 'Bihar', 25.375454, 86.473267, 'Munger, Bihar'),
('Chapra', 'Bihar', 25.780313, 84.747444, 'Chapra, Bihar'),
('Danapur', 'Bihar', 25.629151, 85.042061, 'Danapur, Bihar'),
('Biharsharif', 'Bihar', 25.200249, 85.522102, 'Biharsharif, Bihar'),
('Sasaram', 'Bihar', 24.951650, 84.029060, 'Sasaram, Bihar'),
('Hajipur', 'Bihar', 25.689816, 85.208927, 'Hajipur, Bihar'),
('Dehri', 'Bihar', 24.906464, 84.182312, 'Dehri, Bihar'),
('Siwan', 'Bihar', 26.219110, 84.356445, 'Siwan, Bihar'),
('Motihari', 'Bihar', 26.652179, 84.901093, 'Motihari, Bihar'),
('Nawada', 'Bihar', 24.883318, 85.544525, 'Nawada, Bihar'),
('Bagaha', 'Bihar', 27.096912, 84.093781, 'Bagaha, Bihar'),
('Buxar', 'Bihar', 25.563667, 83.979584, 'Buxar, Bihar'),
('Kishanganj', 'Bihar', 26.106722, 87.943680, 'Kishanganj, Bihar'),
('Sitamarhi', 'Bihar', 26.600654, 85.485390, 'Sitamarhi, Bihar'),
('Jamalpur', 'Bihar', 25.313333, 86.490000, 'Jamalpur, Bihar'),
('Jehanabad', 'Bihar', 25.214722, 84.988611, 'Jehanabad, Bihar'),
('Aurangabad', 'Bihar', 24.753889, 84.374722, 'Aurangabad, Bihar'),
('Madhubani', 'Bihar', 26.354722, 86.073333, 'Madhubani, Bihar'),
('Saharsa', 'Bihar', 25.874722, 86.596667, 'Saharsa, Bihar');

-- CHHATTISGARH
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Raipur', 'Chhattisgarh', 21.251384, 81.629641, 'Raipur, Chhattisgarh'),
('Bhilai', 'Chhattisgarh', 21.209389, 81.428894, 'Bhilai, Chhattisgarh'),
('Bilaspur', 'Chhattisgarh', 22.074721, 82.151158, 'Bilaspur, Chhattisgarh'),
('Korba', 'Chhattisgarh', 22.349274, 82.675781, 'Korba, Chhattisgarh'),
('Durg', 'Chhattisgarh', 21.189985, 81.284927, 'Durg, Chhattisgarh'),
('Rajnandgaon', 'Chhattisgarh', 21.097419, 81.036530, 'Rajnandgaon, Chhattisgarh'),
('Jagdalpur', 'Chhattisgarh', 19.081912, 82.021294, 'Jagdalpur, Chhattisgarh'),
('Raigarh', 'Chhattisgarh', 21.897336, 83.395271, 'Raigarh, Chhattisgarh'),
('Ambikapur', 'Chhattisgarh', 23.119027, 83.193695, 'Ambikapur, Chhattisgarh'),
('Mahasamund', 'Chhattisgarh', 21.107840, 82.094185, 'Mahasamund, Chhattisgarh'),
('Dhamtari', 'Chhattisgarh', 20.707237, 81.546432, 'Dhamtari, Chhattisgarh'),
('Chirmiri', 'Chhattisgarh', 23.212778, 82.415833, 'Chirmiri, Chhattisgarh'),
('Bhatapara', 'Chhattisgarh', 21.740833, 81.949722, 'Bhatapara, Chhattisgarh'),
('Dalli-Rajhara', 'Chhattisgarh', 20.580000, 81.080000, 'Dalli-Rajhara, Chhattisgarh'),
('Naila Janjgir', 'Chhattisgarh', 22.024722, 82.588333, 'Naila Janjgir, Chhattisgarh');

-- GOA
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Panaji', 'Goa', 15.498903, 73.827827, 'Panaji, Goa'),
('Margao', 'Goa', 15.273750, 73.953484, 'Margao, Goa'),
('Vasco da Gama', 'Goa', 15.399349, 73.806580, 'Vasco da Gama, Goa'),
('Mapusa', 'Goa', 15.599722, 73.810833, 'Mapusa, Goa'),
('Ponda', 'Goa', 15.400467, 74.011665, 'Ponda, Goa'),
('Bicholim', 'Goa', 15.595000, 73.950000, 'Bicholim, Goa'),
('Curchorem', 'Goa', 15.264722, 74.105556, 'Curchorem, Goa'),
('Sanquelim', 'Goa', 15.570000, 74.000000, 'Sanquelim, Goa'),
('Pernem', 'Goa', 15.721111, 73.796111, 'Pernem, Goa'),
('Quepem', 'Goa', 15.212222, 74.072222, 'Quepem, Goa');

-- GUJARAT
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Ahmedabad', 'Gujarat', 23.033863, 72.585022, 'Ahmedabad, Gujarat'),
('Surat', 'Gujarat', 21.170240, 72.831062, 'Surat, Gujarat'),
('Vadodara', 'Gujarat', 22.307159, 73.181219, 'Vadodara, Gujarat'),
('Rajkot', 'Gujarat', 22.303894, 70.802162, 'Rajkot, Gujarat'),
('Bhavnagar', 'Gujarat', 21.764310, 72.151642, 'Bhavnagar, Gujarat'),
('Jamnagar', 'Gujarat', 22.471520, 70.057152, 'Jamnagar, Gujarat'),
('Junagadh', 'Gujarat', 21.522179, 70.457824, 'Junagadh, Gujarat'),
('Gandhinagar', 'Gujarat', 23.216667, 72.683333, 'Gandhinagar, Gujarat'),
('Gandhidham', 'Gujarat', 23.083332, 70.133331, 'Gandhidham, Gujarat'),
('Anand', 'Gujarat', 22.556465, 72.951897, 'Anand, Gujarat'),
('Morbi', 'Gujarat', 22.817070, 70.836777, 'Morbi, Gujarat'),
('Nadiad', 'Gujarat', 22.693333, 72.858889, 'Nadiad, Gujarat'),
('Surendranagar', 'Gujarat', 22.703333, 71.636944, 'Surendranagar, Gujarat'),
('Bharuch', 'Gujarat', 21.705240, 72.995956, 'Bharuch, Gujarat'),
('Mehsana', 'Gujarat', 23.597223, 72.368896, 'Mehsana, Gujarat'),
('Porbandar', 'Gujarat', 21.641667, 69.600000, 'Porbandar, Gujarat'),
('Palanpur', 'Gujarat', 24.171250, 72.438332, 'Palanpur, Gujarat'),
('Valsad', 'Gujarat', 20.608889, 72.933056, 'Valsad, Gujarat'),
('Vapi', 'Gujarat', 20.371111, 72.904722, 'Vapi, Gujarat'),
('Navsari', 'Gujarat', 20.850000, 72.916667, 'Navsari, Gujarat'),
('Veraval', 'Gujarat', 20.907778, 70.367222, 'Veraval, Gujarat'),
('Ankleshwar', 'Gujarat', 21.630000, 73.010000, 'Ankleshwar, Gujarat'),
('Godhra', 'Gujarat', 22.775000, 73.615000, 'Godhra, Gujarat'),
('Dahod', 'Gujarat', 22.834444, 74.253889, 'Dahod, Gujarat'),
('Botad', 'Gujarat', 22.169444, 71.666667, 'Botad, Gujarat'),
('Amreli', 'Gujarat', 21.598889, 71.213056, 'Amreli, Gujarat'),
('Deesa', 'Gujarat', 24.259722, 72.186944, 'Deesa, Gujarat'),
('Jetpur', 'Gujarat', 21.754722, 70.623056, 'Jetpur, Gujarat');

-- HARYANA
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Faridabad', 'Haryana', 28.408348, 77.318375, 'Faridabad, Haryana'),
('Gurgaon', 'Haryana', 28.459497, 77.026634, 'Gurgaon, Haryana'),
('Panipat', 'Haryana', 29.387759, 76.968294, 'Panipat, Haryana'),
('Ambala', 'Haryana', 30.378179, 76.771812, 'Ambala, Haryana'),
('Yamunanagar', 'Haryana', 30.129047, 77.284027, 'Yamunanagar, Haryana'),
('Rohtak', 'Haryana', 28.895142, 76.589367, 'Rohtak, Haryana'),
('Hisar', 'Haryana', 29.153862, 75.725891, 'Hisar, Haryana'),
('Karnal', 'Haryana', 29.685381, 76.990494, 'Karnal, Haryana'),
('Sonipat', 'Haryana', 28.994847, 77.015152, 'Sonipat, Haryana'),
('Panchkula', 'Haryana', 30.698409, 76.853454, 'Panchkula, Haryana'),
('Bhiwani', 'Haryana', 28.790196, 76.141396, 'Bhiwani, Haryana'),
('Sirsa', 'Haryana', 29.534534, 75.028885, 'Sirsa, Haryana'),
('Bahadurgarh', 'Haryana', 28.693056, 76.938056, 'Bahadurgarh, Haryana'),
('Jind', 'Haryana', 29.315833, 76.312778, 'Jind, Haryana'),
('Thanesar', 'Haryana', 29.973056, 76.832778, 'Thanesar, Haryana'),
('Kaithal', 'Haryana', 29.801111, 76.400833, 'Kaithal, Haryana'),
('Rewari', 'Haryana', 28.198889, 76.618889, 'Rewari, Haryana'),
('Palwal', 'Haryana', 28.144444, 77.325833, 'Palwal, Haryana'),
('Pundri', 'Haryana', 29.760000, 76.560000, 'Pundri, Haryana'),
('Kosli', 'Haryana', 28.316667, 76.633333, 'Kosli, Haryana');

-- HIMACHAL PRADESH
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Shimla', 'Himachal Pradesh', 31.104815, 77.173340, 'Shimla, Himachal Pradesh'),
('Dharamshala', 'Himachal Pradesh', 32.219265, 76.323340, 'Dharamshala, Himachal Pradesh'),
('Solan', 'Himachal Pradesh', 30.907222, 77.099444, 'Solan, Himachal Pradesh'),
('Mandi', 'Himachal Pradesh', 31.708333, 76.931389, 'Mandi, Himachal Pradesh'),
('Palampur', 'Himachal Pradesh', 32.111111, 76.535833, 'Palampur, Himachal Pradesh'),
('Baddi', 'Himachal Pradesh', 30.958611, 76.794444, 'Baddi, Himachal Pradesh'),
('Nahan', 'Himachal Pradesh', 30.559000, 77.295000, 'Nahan, Himachal Pradesh'),
('Kullu', 'Himachal Pradesh', 31.958056, 77.109444, 'Kullu, Himachal Pradesh'),
('Hamirpur', 'Himachal Pradesh', 31.683333, 76.516667, 'Hamirpur, Himachal Pradesh'),
('Una', 'Himachal Pradesh', 31.465000, 76.270000, 'Una, Himachal Pradesh'),
('Bilaspur', 'Himachal Pradesh', 31.333333, 76.750000, 'Bilaspur, Himachal Pradesh'),
('Chamba', 'Himachal Pradesh', 32.552222, 76.126111, 'Chamba, Himachal Pradesh'),
('Kangra', 'Himachal Pradesh', 32.099722, 76.269167, 'Kangra, Himachal Pradesh'),
('Sundernagar', 'Himachal Pradesh', 31.533056, 76.894444, 'Sundernagar, Himachal Pradesh'),
('Rampur', 'Himachal Pradesh', 31.445000, 77.630000, 'Rampur, Himachal Pradesh');

-- JHARKHAND
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Ranchi', 'Jharkhand', 23.344315, 85.296013, 'Ranchi, Jharkhand'),
('Jamshedpur', 'Jharkhand', 22.805618, 86.203407, 'Jamshedpur, Jharkhand'),
('Dhanbad', 'Jharkhand', 23.798484, 86.450622, 'Dhanbad, Jharkhand'),
('Bokaro Steel City', 'Jharkhand', 23.669296, 86.151112, 'Bokaro Steel City, Jharkhand'),
('Deoghar', 'Jharkhand', 24.486635, 86.694801, 'Deoghar, Jharkhand'),
('Hazaribagh', 'Jharkhand', 23.991944, 85.361389, 'Hazaribagh, Jharkhand'),
('Giridih', 'Jharkhand', 24.191944, 86.304722, 'Giridih, Jharkhand'),
('Ramgarh', 'Jharkhand', 23.631111, 85.520833, 'Ramgarh, Jharkhand'),
('Medininagar', 'Jharkhand', 24.018056, 84.065556, 'Medininagar, Jharkhand'),
('Chirkunda', 'Jharkhand', 23.725833, 86.725833, 'Chirkunda, Jharkhand'),
('Phusro', 'Jharkhand', 23.681389, 86.008056, 'Phusro, Jharkhand'),
('Adityapur', 'Jharkhand', 22.804444, 86.041667, 'Adityapur, Jharkhand'),
('Chaibasa', 'Jharkhand', 22.554722, 85.810000, 'Chaibasa, Jharkhand'),
('Jhumri Tilaiya', 'Jharkhand', 24.433889, 85.527222, 'Jhumri Tilaiya, Jharkhand'),
('Garhwa', 'Jharkhand', 24.162500, 83.805278, 'Garhwa, Jharkhand'),
('Dumka', 'Jharkhand', 24.267778, 87.249444, 'Dumka, Jharkhand'),
('Sahibganj', 'Jharkhand', 25.243611, 87.641944, 'Sahibganj, Jharkhand'),
('Pakur', 'Jharkhand', 24.633611, 87.847778, 'Pakur, Jharkhand'),
('Godda', 'Jharkhand', 24.825833, 87.213611, 'Godda, Jharkhand');

-- KARNATAKA
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Bengaluru', 'Karnataka', 12.971599, 77.594566, 'Bengaluru, Karnataka'),
('Mysuru', 'Karnataka', 12.295810, 76.639381, 'Mysuru, Karnataka'),
('Hubballi', 'Karnataka', 15.364708, 75.123955, 'Hubballi, Karnataka'),
('Mangaluru', 'Karnataka', 12.914142, 74.856018, 'Mangaluru, Karnataka'),
('Belagavi', 'Karnataka', 15.852792, 74.498703, 'Belagavi, Karnataka'),
('Davangere', 'Karnataka', 14.464349, 75.921745, 'Davangere, Karnataka'),
('Ballari', 'Karnataka', 15.143472, 76.923271, 'Ballari, Karnataka'),
('Vijayapura', 'Karnataka', 16.830017, 75.710002, 'Vijayapura, Karnataka'),
('Shivamogga', 'Karnataka', 13.932335, 75.568101, 'Shivamogga, Karnataka'),
('Tumakuru', 'Karnataka', 13.339820, 77.101753, 'Tumakuru, Karnataka'),
('Raichur', 'Karnataka', 16.207298, 77.356415, 'Raichur, Karnataka'),
('Kalaburagi', 'Karnataka', 17.329731, 76.834298, 'Kalaburagi, Karnataka'),
('Kolar', 'Karnataka', 13.136778, 78.129753, 'Kolar, Karnataka'),
('Mandya', 'Karnataka', 12.524444, 76.895556, 'Mandya, Karnataka'),
('Hassan', 'Karnataka', 13.005556, 76.103333, 'Hassan, Karnataka'),
('Udupi', 'Karnataka', 13.338889, 74.746111, 'Udupi, Karnataka'),
('Chikkamagaluru', 'Karnataka', 13.316667, 75.766667, 'Chikkamagaluru, Karnataka'),
('Karwar', 'Karnataka', 14.813611, 74.129444, 'Karwar, Karnataka'),
('Chitradurga', 'Karnataka', 14.221944, 76.401111, 'Chitradurga, Karnataka'),
('Hospet', 'Karnataka', 15.269444, 76.387500, 'Hospet, Karnataka'),
('Gadag-Betigeri', 'Karnataka', 15.426667, 75.635278, 'Gadag-Betigeri, Karnataka'),
('Robertsonpet', 'Karnataka', 12.958333, 78.270000, 'Robertsonpet, Karnataka'),
('Bhadravati', 'Karnataka', 13.846944, 75.703889, 'Bhadravati, Karnataka'),
('Ranebennuru', 'Karnataka', 14.615000, 75.628889, 'Ranebennuru, Karnataka'),
('Bidar', 'Karnataka', 17.913333, 77.530000, 'Bidar, Karnataka'),
('Bagalkot', 'Karnataka', 16.180000, 75.695833, 'Bagalkot, Karnataka'),
('Yadgir', 'Karnataka', 16.770000, 77.137778, 'Yadgir, Karnataka'),
('Chamarajanagar', 'Karnataka', 11.926667, 76.943056, 'Chamarajanagar, Karnataka');

-- KERALA
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Thiruvananthapuram', 'Kerala', 8.524139, 76.936638, 'Thiruvananthapuram, Kerala'),
('Kochi', 'Kerala', 9.931233, 76.267303, 'Kochi, Kerala'),
('Kozhikode', 'Kerala', 11.258753, 75.780411, 'Kozhikode, Kerala'),
('Thrissur', 'Kerala', 10.527640, 76.214420, 'Thrissur, Kerala'),
('Kollam', 'Kerala', 8.881302, 76.584061, 'Kollam, Kerala'),
('Palakkad', 'Kerala', 10.786667, 76.654444, 'Palakkad, Kerala'),
('Alappuzha', 'Kerala', 9.498066, 76.338947, 'Alappuzha, Kerala'),
('Malappuram', 'Kerala', 11.043611, 76.080833, 'Malappuram, Kerala'),
('Kannur', 'Kerala', 11.868890, 75.370369, 'Kannur, Kerala'),
('Kottayam', 'Kerala', 9.591667, 76.522222, 'Kottayam, Kerala'),
('Kasaragod', 'Kerala', 12.496944, 74.988889, 'Kasaragod, Kerala'),
('Pathanamthitta', 'Kerala', 9.266667, 76.783333, 'Pathanamthitta, Kerala'),
('Idukki', 'Kerala', 9.850000, 77.000000, 'Idukki, Kerala'),
('Wayanad', 'Kerala', 11.605000, 76.083333, 'Wayanad, Kerala'),
('Thalassery', 'Kerala', 11.750000, 75.500000, 'Thalassery, Kerala'),
('Ponnani', 'Kerala', 10.767222, 75.925556, 'Ponnani, Kerala'),
('Vatakara', 'Kerala', 11.610000, 75.583333, 'Vatakara, Kerala'),
('Kanhangad', 'Kerala', 12.302778, 75.100556, 'Kanhangad, Kerala'),
('Kayamkulam', 'Kerala', 9.173889, 76.501111, 'Kayamkulam, Kerala'),
('Nedumangad', 'Kerala', 8.600556, 77.001667, 'Nedumangad, Kerala'),
('Changanassery', 'Kerala', 9.443889, 76.539444, 'Changanassery, Kerala'),
('Tirur', 'Kerala', 10.912500, 75.921667, 'Tirur, Kerala'),
('Koyilandy', 'Kerala', 11.437778, 75.695000, 'Koyilandy, Kerala'),
('Thrippunithura', 'Kerala', 9.941111, 76.346111, 'Thrippunithura, Kerala'),
('Paravur', 'Kerala', 10.161667, 76.217222, 'Paravur, Kerala');

-- MADHYA PRADESH
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Indore', 'Madhya Pradesh', 22.719568, 75.857727, 'Indore, Madhya Pradesh'),
('Bhopal', 'Madhya Pradesh', 23.259933, 77.412613, 'Bhopal, Madhya Pradesh'),
('Jabalpur', 'Madhya Pradesh', 23.181467, 79.9864, 'Jabalpur, Madhya Pradesh'),
('Gwalior', 'Madhya Pradesh', 26.218287, 78.182831, 'Gwalior, Madhya Pradesh'),
('Ujjain', 'Madhya Pradesh', 23.182384, 75.776329, 'Ujjain, Madhya Pradesh'),
('Sagar', 'Madhya Pradesh', 23.838405, 78.738442, 'Sagar, Madhya Pradesh'),
('Dewas', 'Madhya Pradesh', 22.965791, 76.050781, 'Dewas, Madhya Pradesh'),
('Satna', 'Madhya Pradesh', 24.600556, 80.832222, 'Satna, Madhya Pradesh'),
('Ratlam', 'Madhya Pradesh', 23.330000, 75.040000, 'Ratlam, Madhya Pradesh'),
('Rewa', 'Madhya Pradesh', 24.533333, 81.300000, 'Rewa, Madhya Pradesh'),
('Murwara', 'Madhya Pradesh', 23.838889, 80.396111, 'Murwara, Madhya Pradesh'),
('Singrauli', 'Madhya Pradesh', 24.200000, 82.676389, 'Singrauli, Madhya Pradesh'),
('Burhanpur', 'Madhya Pradesh', 21.309167, 76.228889, 'Burhanpur, Madhya Pradesh'),
('Khandwa', 'Madhya Pradesh', 21.823056, 76.358889, 'Khandwa, Madhya Pradesh'),
('Bhind', 'Madhya Pradesh', 26.564444, 78.778889, 'Bhind, Madhya Pradesh'),
('Chhindwara', 'Madhya Pradesh', 22.057222, 78.939444, 'Chhindwara, Madhya Pradesh'),
('Guna', 'Madhya Pradesh', 24.647778, 77.312222, 'Guna, Madhya Pradesh'),
('Shivpuri', 'Madhya Pradesh', 25.423611, 77.659722, 'Shivpuri, Madhya Pradesh'),
('Vidisha', 'Madhya Pradesh', 23.525278, 77.808333, 'Vidisha, Madhya Pradesh'),
('Chhatarpur', 'Madhya Pradesh', 24.912222, 79.592222, 'Chhatarpur, Madhya Pradesh'),
('Damoh', 'Madhya Pradesh', 23.833056, 79.442222, 'Damoh, Madhya Pradesh'),
('Mandsaur', 'Madhya Pradesh', 24.076389, 75.071111, 'Mandsaur, Madhya Pradesh'),
('Khargone', 'Madhya Pradesh', 21.823056, 75.613611, 'Khargone, Madhya Pradesh'),
('Neemuch', 'Madhya Pradesh', 24.469167, 74.874444, 'Neemuch, Madhya Pradesh'),
('Pithampur', 'Madhya Pradesh', 22.607222, 75.688611, 'Pithampur, Madhya Pradesh'),
('Hoshangabad', 'Madhya Pradesh', 22.750000, 77.730000, 'Hoshangabad, Madhya Pradesh'),
('Itarsi', 'Madhya Pradesh', 22.614444, 77.764167, 'Itarsi, Madhya Pradesh'),
('Sehore', 'Madhya Pradesh', 23.200000, 77.083333, 'Sehore, Madhya Pradesh'),
('Betul', 'Madhya Pradesh', 21.900000, 77.900000, 'Betul, Madhya Pradesh'),
('Seoni', 'Madhya Pradesh', 22.085833, 79.550000, 'Seoni, Madhya Pradesh'),
('Datia', 'Madhya Pradesh', 25.671389, 78.462778, 'Datia, Madhya Pradesh'),
('Nagda', 'Madhya Pradesh', 23.458056, 75.418611, 'Nagda, Madhya Pradesh');

-- MAHARASHTRA
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Mumbai', 'Maharashtra', 19.075983, 72.877655, 'Mumbai, Maharashtra'),
('Pune', 'Maharashtra', 18.520430, 73.856743, 'Pune, Maharashtra'),
('Nagpur', 'Maharashtra', 21.145800, 79.088158, 'Nagpur, Maharashtra'),
('Thane', 'Maharashtra', 19.218330, 72.978088, 'Thane, Maharashtra'),
('Nashik', 'Maharashtra', 19.997454, 73.789803, 'Nashik, Maharashtra'),
('Aurangabad', 'Maharashtra', 19.876165, 75.343315, 'Aurangabad, Maharashtra'),
('Solapur', 'Maharashtra', 17.671692, 75.906387, 'Solapur, Maharashtra'),
('Amravati', 'Maharashtra', 20.933272, 77.752090, 'Amravati, Maharashtra'),
('Kolhapur', 'Maharashtra', 16.705193, 74.243309, 'Kolhapur, Maharashtra'),
('Navi Mumbai', 'Maharashtra', 19.033058, 73.029662, 'Navi Mumbai, Maharashtra'),
('Sangli', 'Maharashtra', 16.854820, 74.568363, 'Sangli, Maharashtra'),
('Malegaon', 'Maharashtra', 20.563333, 74.528889, 'Malegaon, Maharashtra'),
('Jalgaon', 'Maharashtra', 21.010000, 75.563333, 'Jalgaon, Maharashtra'),
('Akola', 'Maharashtra', 20.700000, 77.000000, 'Akola, Maharashtra'),
('Latur', 'Maharashtra', 18.400000, 76.583333, 'Latur, Maharashtra'),
('Dhule', 'Maharashtra', 20.901944, 74.777500, 'Dhule, Maharashtra'),
('Ahmednagar', 'Maharashtra', 19.094677, 74.738960, 'Ahmednagar, Maharashtra'),
('Chandrapur', 'Maharashtra', 19.950000, 79.300000, 'Chandrapur, Maharashtra'),
('Parbhani', 'Maharashtra', 19.268333, 76.770833, 'Parbhani, Maharashtra'),
('Ichalkaranji', 'Maharashtra', 16.691944, 74.460833, 'Ichalkaranji, Maharashtra'),
('Jalna', 'Maharashtra', 19.834444, 75.880833, 'Jalna, Maharashtra'),
('Ambarnath', 'Maharashtra', 19.192222, 73.198889, 'Ambarnath, Maharashtra'),
('Bhusawal', 'Maharashtra', 21.044444, 75.785278, 'Bhusawal, Maharashtra'),
('Panvel', 'Maharashtra', 18.989167, 73.111389, 'Panvel, Maharashtra'),
('Satara', 'Maharashtra', 17.686111, 74.018611, 'Satara, Maharashtra'),
('Beed', 'Maharashtra', 18.989722, 75.755556, 'Beed, Maharashtra'),
('Yavatmal', 'Maharashtra', 20.391389, 78.123889, 'Yavatmal, Maharashtra'),
('Kamptee', 'Maharashtra', 21.221111, 79.211389, 'Kamptee, Maharashtra'),
('Gondia', 'Maharashtra', 21.460000, 80.200000, 'Gondia, Maharashtra'),
('Barshi', 'Maharashtra', 18.236111, 75.693889, 'Barshi, Maharashtra'),
('Achalpur', 'Maharashtra', 21.258056, 77.510000, 'Achalpur, Maharashtra'),
('Osmanabad', 'Maharashtra', 18.183333, 76.050000, 'Osmanabad, Maharashtra'),
('Nanded', 'Maharashtra', 19.150000, 77.316667, 'Nanded, Maharashtra'),
('Wardha', 'Maharashtra', 20.750000, 78.600000, 'Wardha, Maharashtra'),
('Udgir', 'Maharashtra', 18.393333, 77.116667, 'Udgir, Maharashtra'),
('Hinganghat', 'Maharashtra', 20.548889, 78.834167, 'Hinganghat, Maharashtra');

-- MANIPUR
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Imphal', 'Manipur', 24.817615, 93.936939, 'Imphal, Manipur'),
('Thoubal', 'Manipur', 24.633333, 94.000000, 'Thoubal, Manipur'),
('Bishnupur', 'Manipur', 24.583333, 93.766667, 'Bishnupur, Manipur'),
('Churachandpur', 'Manipur', 24.331111, 93.678889, 'Churachandpur, Manipur'),
('Senapati', 'Manipur', 25.267222, 94.027778, 'Senapati, Manipur'),
('Ukhrul', 'Manipur', 25.066667, 94.366667, 'Ukhrul, Manipur'),
('Chandel', 'Manipur', 24.325000, 94.025000, 'Chandel, Manipur'),
('Kakching', 'Manipur', 24.500000, 93.983333, 'Kakching, Manipur'),
('Jiribam', 'Manipur', 24.806944, 93.110556, 'Jiribam, Manipur'),
('Moirang', 'Manipur', 24.500000, 93.766667, 'Moirang, Manipur');

-- MEGHALAYA
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Shillong', 'Meghalaya', 25.578773, 91.893257, 'Shillong, Meghalaya'),
('Tura', 'Meghalaya', 25.513889, 90.206667, 'Tura, Meghalaya'),
('Nongstoin', 'Meghalaya', 25.516667, 91.266667, 'Nongstoin, Meghalaya'),
('Jowai', 'Meghalaya', 25.450000, 92.200000, 'Jowai, Meghalaya'),
('Williamnagar', 'Meghalaya', 25.489167, 90.140000, 'Williamnagar, Meghalaya'),
('Baghmara', 'Meghalaya', 25.183333, 90.650000, 'Baghmara, Meghalaya'),
('Nongpoh', 'Meghalaya', 25.900000, 91.883333, 'Nongpoh, Meghalaya');

-- MIZORAM
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Aizawl', 'Mizoram', 23.727106, 92.717636, 'Aizawl, Mizoram'),
('Lunglei', 'Mizoram', 22.883333, 92.733333, 'Lunglei, Mizoram'),
('Champhai', 'Mizoram', 23.466667, 93.333333, 'Champhai, Mizoram'),
('Serchhip', 'Mizoram', 23.300000, 92.833333, 'Serchhip, Mizoram'),
('Kolasib', 'Mizoram', 24.225000, 92.679722, 'Kolasib, Mizoram'),
('Saiha', 'Mizoram', 22.490833, 92.978611, 'Saiha, Mizoram'),
('Lawngtlai', 'Mizoram', 22.533333, 92.900000, 'Lawngtlai, Mizoram'),
('Mamit', 'Mizoram', 23.751111, 92.476111, 'Mamit, Mizoram');

-- NAGALAND
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Kohima', 'Nagaland', 25.674065, 94.107635, 'Kohima, Nagaland'),
('Dimapur', 'Nagaland', 25.903748, 93.720940, 'Dimapur, Nagaland'),
('Mokokchung', 'Nagaland', 26.322222, 94.520833, 'Mokokchung, Nagaland'),
('Tuensang', 'Nagaland', 26.263889, 94.825556, 'Tuensang, Nagaland'),
('Wokha', 'Nagaland', 26.100000, 94.266667, 'Wokha, Nagaland'),
('Mon', 'Nagaland', 26.730833, 95.075833, 'Mon, Nagaland'),
('Zunheboto', 'Nagaland', 25.970833, 94.516667, 'Zunheboto, Nagaland'),
('Phek', 'Nagaland', 25.669444, 94.500000, 'Phek, Nagaland'),
('Longleng', 'Nagaland', 26.468056, 94.923889, 'Longleng, Nagaland'),
('Kiphire', 'Nagaland', 25.834722, 94.804722, 'Kiphire, Nagaland'),
('Peren', 'Nagaland', 25.520000, 93.730000, 'Peren, Nagaland');

-- ODISHA
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Bhubaneswar', 'Odisha', 20.296059, 85.824539, 'Bhubaneswar, Odisha'),
('Cuttack', 'Odisha', 20.462521, 85.882835, 'Cuttack, Odisha'),
('Rourkela', 'Odisha', 22.224820, 84.854290, 'Rourkela, Odisha'),
('Brahmapur', 'Odisha', 19.311389, 84.792778, 'Brahmapur, Odisha'),
('Sambalpur', 'Odisha', 21.466667, 83.970000, 'Sambalpur, Odisha'),
('Puri', 'Odisha', 19.801389, 85.831111, 'Puri, Odisha'),
('Balasore', 'Odisha', 21.493333, 86.933333, 'Balasore, Odisha'),
('Bhadrak', 'Odisha', 21.058333, 86.515278, 'Bhadrak, Odisha'),
('Baripada', 'Odisha', 21.933333, 86.733333, 'Baripada, Odisha'),
('Jharsuguda', 'Odisha', 21.855556, 84.005278, 'Jharsuguda, Odisha'),
('Jeypore', 'Odisha', 18.866667, 82.566667, 'Jeypore, Odisha'),
('Bargarh', 'Odisha', 21.333333, 83.616667, 'Bargarh, Odisha'),
('Paradip', 'Odisha', 20.316667, 86.600000, 'Paradip, Odisha'),
('Kendujhar', 'Odisha', 21.633333, 85.583333, 'Kendujhar, Odisha'),
('Rayagada', 'Odisha', 19.172222, 83.415556, 'Rayagada, Odisha'),
('Anugul', 'Odisha', 20.839167, 85.098333, 'Anugul, Odisha'),
('Dhenkanal', 'Odisha', 20.650000, 85.599444, 'Dhenkanal, Odisha'),
('Phulbani', 'Odisha', 20.483333, 84.233333, 'Phulbani, Odisha'),
('Balangir', 'Odisha', 20.700000, 83.483333, 'Balangir, Odisha'),
('Koraput', 'Odisha', 18.813056, 82.711944, 'Koraput, Odisha');

-- PUNJAB
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Ludhiana', 'Punjab', 30.901457, 75.857300, 'Ludhiana, Punjab'),
('Amritsar', 'Punjab', 31.633980, 74.872261, 'Amritsar, Punjab'),
('Jalandhar', 'Punjab', 31.325994, 75.576183, 'Jalandhar, Punjab'),
('Patiala', 'Punjab', 30.336204, 76.392162, 'Patiala, Punjab'),
('Bathinda', 'Punjab', 30.210994, 74.945473, 'Bathinda, Punjab'),
('Hoshiarpur', 'Punjab', 31.533611, 75.917778, 'Hoshiarpur, Punjab'),
('Batala', 'Punjab', 31.809444, 75.203056, 'Batala, Punjab'),
('Pathankot', 'Punjab', 32.268333, 75.652222, 'Pathankot, Punjab'),
('Moga', 'Punjab', 30.817778, 75.170278, 'Moga, Punjab'),
('Abohar', 'Punjab', 30.144444, 74.199167, 'Abohar, Punjab'),
('Malerkotla', 'Punjab', 30.531389, 75.880556, 'Malerkotla, Punjab'),
('Khanna', 'Punjab', 30.705556, 76.222222, 'Khanna, Punjab'),
('Mohali', 'Punjab', 30.704649, 76.717873, 'Mohali, Punjab'),
('Barnala', 'Punjab', 30.373056, 75.549167, 'Barnala, Punjab'),
('Firozpur', 'Punjab', 30.928611, 74.613056, 'Firozpur, Punjab'),
('Phagwara', 'Punjab', 31.225000, 75.770833, 'Phagwara, Punjab'),
('Kapurthala', 'Punjab', 31.380000, 75.381111, 'Kapurthala, Punjab'),
('Zirakpur', 'Punjab', 30.638889, 76.817778, 'Zirakpur, Punjab'),
('Kot Kapura', 'Punjab', 30.583056, 74.813333, 'Kot Kapura, Punjab'),
('Faridkot', 'Punjab', 30.674444, 74.756111, 'Faridkot, Punjab'),
('Muktsar', 'Punjab', 30.475556, 74.515556, 'Muktsar, Punjab'),
('Rajpura', 'Punjab', 30.476389, 76.594167, 'Rajpura, Punjab'),
('Sangrur', 'Punjab', 30.245278, 75.840278, 'Sangrur, Punjab'),
('Fazilka', 'Punjab', 30.402778, 74.028611, 'Fazilka, Punjab'),
('Gurdaspur', 'Punjab', 32.038611, 75.404722, 'Gurdaspur, Punjab'),
('Kharar', 'Punjab', 30.743889, 76.646667, 'Kharar, Punjab'),
('Gobindgarh', 'Punjab', 30.670278, 76.301111, 'Gobindgarh, Punjab'),
('Mansa', 'Punjab', 29.987500, 75.393056, 'Mansa, Punjab'),
('Malout', 'Punjab', 30.188333, 74.495278, 'Malout, Punjab'),
('Nawanshahr', 'Punjab', 31.125000, 76.116667, 'Nawanshahr, Punjab');

-- RAJASTHAN
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Jaipur', 'Rajasthan', 26.912434, 75.787270, 'Jaipur, Rajasthan'),
('Jodhpur', 'Rajasthan', 26.238947, 73.024309, 'Jodhpur, Rajasthan'),
('Kota', 'Rajasthan', 25.213890, 75.834839, 'Kota, Rajasthan'),
('Bikaner', 'Rajasthan', 28.016667, 73.300000, 'Bikaner, Rajasthan'),
('Udaipur', 'Rajasthan', 24.585445, 73.712479, 'Udaipur, Rajasthan'),
('Ajmer', 'Rajasthan', 26.449923, 74.639789, 'Ajmer, Rajasthan'),
('Bhilwara', 'Rajasthan', 25.347261, 74.640984, 'Bhilwara, Rajasthan'),
('Alwar', 'Rajasthan', 27.566667, 76.600000, 'Alwar, Rajasthan'),
('Bharatpur', 'Rajasthan', 27.216667, 77.483333, 'Bharatpur, Rajasthan'),
('Pali', 'Rajasthan', 25.771389, 73.323611, 'Pali, Rajasthan'),
('Barmer', 'Rajasthan', 25.750000, 71.400000, 'Barmer, Rajasthan'),
('Sikar', 'Rajasthan', 27.612222, 75.139444, 'Sikar, Rajasthan'),
('Tonk', 'Rajasthan', 26.150000, 75.783333, 'Tonk, Rajasthan'),
('Sadulpur', 'Rajasthan', 27.883333, 74.416667, 'Sadulpur, Rajasthan'),
('Sawai Madhopur', 'Rajasthan', 26.023056, 76.353611, 'Sawai Madhopur, Rajasthan'),
('Nagaur', 'Rajasthan', 27.202222, 73.733333, 'Nagaur, Rajasthan'),
('Makrana', 'Rajasthan', 27.041667, 74.716667, 'Makrana, Rajasthan'),
('Sujangarh', 'Rajasthan', 27.700000, 74.466667, 'Sujangarh, Rajasthan'),
('Sardarshahar', 'Rajasthan', 28.441667, 74.491667, 'Sardarshahar, Rajasthan'),
('Ladnu', 'Rajasthan', 27.650000, 74.400000, 'Ladnu, Rajasthan'),
('Ratangarh', 'Rajasthan', 28.083333, 74.616667, 'Ratangarh, Rajasthan'),
('Nokha', 'Rajasthan', 27.561111, 73.460833, 'Nokha, Rajasthan'),
('Nimbahera', 'Rajasthan', 24.619722, 74.681111, 'Nimbahera, Rajasthan'),
('Suratgarh', 'Rajasthan', 29.321667, 73.900000, 'Suratgarh, Rajasthan'),
('Rajsamand', 'Rajasthan', 25.066667, 73.883333, 'Rajsamand, Rajasthan'),
('Lachhmangarh', 'Rajasthan', 27.825000, 75.031111, 'Lachhmangarh, Rajasthan'),
('Dhaulpur', 'Rajasthan', 26.700000, 77.900000, 'Dhaulpur, Rajasthan'),
('Karauli', 'Rajasthan', 26.500000, 77.033333, 'Karauli, Rajasthan'),
('Gangapur City', 'Rajasthan', 26.470000, 76.733611, 'Gangapur City, Rajasthan'),
('Merta City', 'Rajasthan', 26.640000, 74.034722, 'Merta City, Rajasthan'),
('Chittorgarh', 'Rajasthan', 24.879999, 74.629997, 'Chittorgarh, Rajasthan'),
('Hanumangarh', 'Rajasthan', 29.583333, 74.316667, 'Hanumangarh, Rajasthan'),
('Jaisalmer', 'Rajasthan', 26.916667, 70.916667, 'Jaisalmer, Rajasthan'),
('Jhunjhunu', 'Rajasthan', 28.129167, 75.398056, 'Jhunjhunu, Rajasthan'),
('Sirohi', 'Rajasthan', 24.885833, 72.858333, 'Sirohi, Rajasthan');

-- SIKKIM
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Gangtok', 'Sikkim', 27.338936, 88.606277, 'Gangtok, Sikkim'),
('Namchi', 'Sikkim', 27.165000, 88.363889, 'Namchi, Sikkim'),
('Mangan', 'Sikkim', 27.506667, 88.523889, 'Mangan, Sikkim'),
('Gyalshing', 'Sikkim', 27.289167, 88.056944, 'Gyalshing, Sikkim'),
('Rangpo', 'Sikkim', 27.173056, 88.531111, 'Rangpo, Sikkim'),
('Jorethang', 'Sikkim', 27.106111, 88.416667, 'Jorethang, Sikkim'),
('Singtam', 'Sikkim', 27.233333, 88.500000, 'Singtam, Sikkim'),
('Ravangla', 'Sikkim', 27.313889, 88.119444, 'Ravangla, Sikkim');

-- TAMIL NADU
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Chennai', 'Tamil Nadu', 13.082680, 80.270718, 'Chennai, Tamil Nadu'),
('Coimbatore', 'Tamil Nadu', 11.016844, 76.955832, 'Coimbatore, Tamil Nadu'),
('Madurai', 'Tamil Nadu', 9.925201, 78.119775, 'Madurai, Tamil Nadu'),
('Tiruchirappalli', 'Tamil Nadu', 10.790479, 78.704773, 'Tiruchirappalli, Tamil Nadu'),
('Salem', 'Tamil Nadu', 11.664325, 78.146011, 'Salem, Tamil Nadu'),
('Tirunelveli', 'Tamil Nadu', 8.725211, 77.687973, 'Tirunelveli, Tamil Nadu'),
('Tiruppur', 'Tamil Nadu', 11.107754, 77.341230, 'Tiruppur, Tamil Nadu'),
('Vellore', 'Tamil Nadu', 12.905950, 79.132217, 'Vellore, Tamil Nadu'),
('Erode', 'Tamil Nadu', 11.340796, 77.717957, 'Erode, Tamil Nadu'),
('Thoothukkudi', 'Tamil Nadu', 8.761993, 78.134992, 'Thoothukkudi, Tamil Nadu'),
('Dindigul', 'Tamil Nadu', 10.362099, 77.981567, 'Dindigul, Tamil Nadu'),
('Thanjavur', 'Tamil Nadu', 10.787260, 79.138039, 'Thanjavur, Tamil Nadu'),
('Ranipet', 'Tamil Nadu', 12.926389, 79.333611, 'Ranipet, Tamil Nadu'),
('Sivakasi', 'Tamil Nadu', 9.453056, 77.802222, 'Sivakasi, Tamil Nadu'),
('Karur', 'Tamil Nadu', 10.960000, 78.076667, 'Karur, Tamil Nadu'),
('Kanchipuram', 'Tamil Nadu', 12.835000, 79.700556, 'Kanchipuram, Tamil Nadu'),
('Kumarapalayam', 'Tamil Nadu', 11.445000, 77.270000, 'Kumarapalayam, Tamil Nadu'),
('Neyveli', 'Tamil Nadu', 11.613333, 79.488889, 'Neyveli, Tamil Nadu'),
('Cuddalore', 'Tamil Nadu', 11.749444, 79.763333, 'Cuddalore, Tamil Nadu'),
('Kumbakonam', 'Tamil Nadu', 10.962778, 79.384444, 'Kumbakonam, Tamil Nadu'),
('Tiruvannamalai', 'Tamil Nadu', 12.230556, 79.067222, 'Tiruvannamalai, Tamil Nadu'),
('Pollachi', 'Tamil Nadu', 10.663889, 77.008333, 'Pollachi, Tamil Nadu'),
('Rajapalayam', 'Tamil Nadu', 9.451389, 77.554722, 'Rajapalayam, Tamil Nadu'),
('Gudiyatham', 'Tamil Nadu', 12.947222, 78.874444, 'Gudiyatham, Tamil Nadu'),
('Pudukkottai', 'Tamil Nadu', 10.380000, 78.820000, 'Pudukkottai, Tamil Nadu'),
('Vaniyambadi', 'Tamil Nadu', 12.682778, 78.616944, 'Vaniyambadi, Tamil Nadu'),
('Ambur', 'Tamil Nadu', 12.791667, 78.716667, 'Ambur, Tamil Nadu'),
('Nagapattinam', 'Tamil Nadu', 10.766667, 79.833333, 'Nagapattinam, Tamil Nadu'),
('Nagercoil', 'Tamil Nadu', 8.177778, 77.434444, 'Nagercoil, Tamil Nadu'),
('Hosur', 'Tamil Nadu', 12.731945, 77.831734, 'Hosur, Tamil Nadu'),
('Kancheepuram', 'Tamil Nadu', 12.835000, 79.700556, 'Kancheepuram, Tamil Nadu'),
('Arakkonam', 'Tamil Nadu', 13.083333, 79.666667, 'Arakkonam, Tamil Nadu'),
('Tindivanam', 'Tamil Nadu', 12.233333, 79.650000, 'Tindivanam, Tamil Nadu'),
('Virudhunagar', 'Tamil Nadu', 9.583333, 77.950000, 'Virudhunagar, Tamil Nadu'),
('Krishnagiri', 'Tamil Nadu', 12.516667, 78.216667, 'Krishnagiri, Tamil Nadu'),
('Karaikudi', 'Tamil Nadu', 10.066667, 78.783333, 'Karaikudi, Tamil Nadu'),
('Dharmapuri', 'Tamil Nadu', 12.120000, 78.160000, 'Dharmapuri, Tamil Nadu'),
('Namakkal', 'Tamil Nadu', 11.233333, 78.166667, 'Namakkal, Tamil Nadu'),
('Chengalpattu', 'Tamil Nadu', 12.683333, 79.983333, 'Chengalpattu, Tamil Nadu'),
('Tenkasi', 'Tamil Nadu', 8.960000, 77.316667, 'Tenkasi, Tamil Nadu');

-- TELANGANA
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Hyderabad', 'Telangana', 17.385044, 78.486671, 'Hyderabad, Telangana'),
('Warangal', 'Telangana', 17.968731, 79.594454, 'Warangal, Telangana'),
('Nizamabad', 'Telangana', 18.671797, 78.093849, 'Nizamabad, Telangana'),
('Khammam', 'Telangana', 17.247623, 80.143814, 'Khammam, Telangana'),
('Karimnagar', 'Telangana', 18.439225, 79.128630, 'Karimnagar, Telangana'),
('Ramagundam', 'Telangana', 18.755139, 79.474139, 'Ramagundam, Telangana'),
('Mahbubnagar', 'Telangana', 16.739886, 77.987808, 'Mahbubnagar, Telangana'),
('Nalgonda', 'Telangana', 17.055000, 79.268056, 'Nalgonda, Telangana'),
('Adilabad', 'Telangana', 19.667222, 78.533333, 'Adilabad, Telangana'),
('Suryapet', 'Telangana', 17.139722, 79.618889, 'Suryapet, Telangana'),
('Siddipet', 'Telangana', 18.104722, 78.850556, 'Siddipet, Telangana'),
('Miryalaguda', 'Telangana', 16.866667, 79.566667, 'Miryalaguda, Telangana'),
('Jagtial', 'Telangana', 18.793611, 78.911389, 'Jagtial, Telangana'),
('Mancherial', 'Telangana', 18.868611, 79.462778, 'Mancherial, Telangana'),
('Nirmal', 'Telangana', 19.097222, 78.343611, 'Nirmal, Telangana'),
('Kamareddy', 'Telangana', 18.321667, 78.341111, 'Kamareddy, Telangana'),
('Bodhan', 'Telangana', 18.666667, 77.883333, 'Bodhan, Telangana'),
('Sangareddy', 'Telangana', 17.620000, 78.083333, 'Sangareddy, Telangana'),
('Metpally', 'Telangana', 18.833056, 78.575000, 'Metpally, Telangana'),
('Zaheerabad', 'Telangana', 17.683889, 77.606111, 'Zaheerabad, Telangana'),
('Bhongir', 'Telangana', 17.516667, 78.883333, 'Bhongir, Telangana'),
('Kothagudem', 'Telangana', 17.550556, 80.618056, 'Kothagudem, Telangana'),
('Palwancha', 'Telangana', 17.583333, 80.683333, 'Palwancha, Telangana'),
('Wanaparthy', 'Telangana', 16.367500, 78.067778, 'Wanaparthy, Telangana'),
('Gadwal', 'Telangana', 16.233333, 77.800000, 'Gadwal, Telangana');

-- TRIPURA
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Agartala', 'Tripura', 23.836050, 91.279386, 'Agartala, Tripura'),
('Dharmanagar', 'Tripura', 24.370000, 92.170000, 'Dharmanagar, Tripura'),
('Udaipur', 'Tripura', 23.533333, 91.483333, 'Udaipur, Tripura'),
('Kailashahar', 'Tripura', 24.331944, 92.003889, 'Kailashahar, Tripura'),
('Belonia', 'Tripura', 23.250000, 91.450000, 'Belonia, Tripura'),
('Khowai', 'Tripura', 24.066667, 91.600000, 'Khowai, Tripura'),
('Ambassa', 'Tripura', 23.933333, 91.850000, 'Ambassa, Tripura'),
('Teliamura', 'Tripura', 23.833333, 91.733333, 'Teliamura, Tripura');

-- UTTAR PRADESH
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Lucknow', 'Uttar Pradesh', 26.846694, 80.946166, 'Lucknow, Uttar Pradesh'),
('Kanpur', 'Uttar Pradesh', 26.449923, 80.331871, 'Kanpur, Uttar Pradesh'),
('Ghaziabad', 'Uttar Pradesh', 28.669155, 77.453758, 'Ghaziabad, Uttar Pradesh'),
('Agra', 'Uttar Pradesh', 27.176670, 78.008075, 'Agra, Uttar Pradesh'),
('Varanasi', 'Uttar Pradesh', 25.317645, 82.973914, 'Varanasi, Uttar Pradesh'),
('Meerut', 'Uttar Pradesh', 28.984644, 77.705872, 'Meerut, Uttar Pradesh'),
('Allahabad', 'Uttar Pradesh', 25.435801, 81.846311, 'Allahabad, Uttar Pradesh'),
('Bareilly', 'Uttar Pradesh', 28.364449, 79.415214, 'Bareilly, Uttar Pradesh'),
('Aligarh', 'Uttar Pradesh', 27.897439, 78.088425, 'Aligarh, Uttar Pradesh'),
('Moradabad', 'Uttar Pradesh', 28.839104, 78.776857, 'Moradabad, Uttar Pradesh'),
('Saharanpur', 'Uttar Pradesh', 29.967968, 77.545683, 'Saharanpur, Uttar Pradesh'),
('Gorakhpur', 'Uttar Pradesh', 26.754783, 83.373047, 'Gorakhpur, Uttar Pradesh'),
('Noida', 'Uttar Pradesh', 28.535517, 77.391029, 'Noida, Uttar Pradesh'),
('Firozabad', 'Uttar Pradesh', 27.150000, 78.400000, 'Firozabad, Uttar Pradesh'),
('Jhansi', 'Uttar Pradesh', 25.448389, 78.569722, 'Jhansi, Uttar Pradesh'),
('Muzaffarnagar', 'Uttar Pradesh', 29.470308, 77.703236, 'Muzaffarnagar, Uttar Pradesh'),
('Mathura', 'Uttar Pradesh', 27.492413, 77.673673, 'Mathura, Uttar Pradesh'),
('Budaun', 'Uttar Pradesh', 28.034444, 79.113889, 'Budaun, Uttar Pradesh'),
('Rampur', 'Uttar Pradesh', 28.802608, 79.025177, 'Rampur, Uttar Pradesh'),
('Shahjahanpur', 'Uttar Pradesh', 27.881667, 79.905278, 'Shahjahanpur, Uttar Pradesh'),
('Farrukhabad', 'Uttar Pradesh', 27.397500, 79.580833, 'Farrukhabad, Uttar Pradesh'),
('Ayodhya', 'Uttar Pradesh', 26.767414, 82.202477, 'Ayodhya, Uttar Pradesh'),
('Mau', 'Uttar Pradesh', 25.941667, 83.560000, 'Mau, Uttar Pradesh'),
('Hapur', 'Uttar Pradesh', 28.729722, 77.776111, 'Hapur, Uttar Pradesh'),
('Etawah', 'Uttar Pradesh', 26.785556, 79.023056, 'Etawah, Uttar Pradesh'),
('Mirzapur', 'Uttar Pradesh', 25.145833, 82.565000, 'Mirzapur, Uttar Pradesh'),
('Bulandshahr', 'Uttar Pradesh', 28.405556, 77.857778, 'Bulandshahr, Uttar Pradesh'),
('Sambhal', 'Uttar Pradesh', 28.585278, 78.570278, 'Sambhal, Uttar Pradesh'),
('Amroha', 'Uttar Pradesh', 28.903889, 78.466944, 'Amroha, Uttar Pradesh'),
('Hardoi', 'Uttar Pradesh', 27.397222, 80.131389, 'Hardoi, Uttar Pradesh'),
('Fatehpur', 'Uttar Pradesh', 25.931389, 80.808889, 'Fatehpur, Uttar Pradesh'),
('Raebareli', 'Uttar Pradesh', 26.232222, 81.234722, 'Raebareli, Uttar Pradesh'),
('Orai', 'Uttar Pradesh', 25.990000, 79.450000, 'Orai, Uttar Pradesh'),
('Sitapur', 'Uttar Pradesh', 27.566111, 80.683889, 'Sitapur, Uttar Pradesh'),
('Bahraich', 'Uttar Pradesh', 27.575278, 81.594722, 'Bahraich, Uttar Pradesh'),
('Modinagar', 'Uttar Pradesh', 28.830278, 77.616389, 'Modinagar, Uttar Pradesh'),
('Unnao', 'Uttar Pradesh', 26.545833, 80.488056, 'Unnao, Uttar Pradesh'),
('Jaunpur', 'Uttar Pradesh', 25.735833, 82.692778, 'Jaunpur, Uttar Pradesh'),
('Lakhimpur', 'Uttar Pradesh', 27.948056, 80.778889, 'Lakhimpur, Uttar Pradesh'),
('Hathras', 'Uttar Pradesh', 27.596389, 78.049444, 'Hathras, Uttar Pradesh'),
('Banda', 'Uttar Pradesh', 25.477222, 80.336389, 'Banda, Uttar Pradesh'),
('Pilibhit', 'Uttar Pradesh', 28.633333, 79.811111, 'Pilibhit, Uttar Pradesh'),
('Barabanki', 'Uttar Pradesh', 26.922500, 81.185000, 'Barabanki, Uttar Pradesh'),
('Khurja', 'Uttar Pradesh', 28.254167, 77.855833, 'Khurja, Uttar Pradesh'),
('Gonda', 'Uttar Pradesh', 27.133333, 81.961111, 'Gonda, Uttar Pradesh'),
('Mainpuri', 'Uttar Pradesh', 27.222222, 79.032222, 'Mainpuri, Uttar Pradesh'),
('Lalitpur', 'Uttar Pradesh', 24.688056, 78.415833, 'Lalitpur, Uttar Pradesh'),
('Etah', 'Uttar Pradesh', 27.634722, 78.659444, 'Etah, Uttar Pradesh'),
('Deoria', 'Uttar Pradesh', 26.501667, 83.778889, 'Deoria, Uttar Pradesh'),
('Azamgarh', 'Uttar Pradesh', 26.067778, 83.183333, 'Azamgarh, Uttar Pradesh'),
('Ballia', 'Uttar Pradesh', 25.766667, 84.149722, 'Ballia, Uttar Pradesh'),
('Basti', 'Uttar Pradesh', 26.800556, 82.734722, 'Basti, Uttar Pradesh'),
('Chandausi', 'Uttar Pradesh', 28.450000, 78.783333, 'Chandausi, Uttar Pradesh'),
('Akbarpur', 'Uttar Pradesh', 26.430000, 82.533333, 'Akbarpur, Uttar Pradesh'),
('Kasganj', 'Uttar Pradesh', 27.805000, 78.645000, 'Kasganj, Uttar Pradesh');

-- UTTARAKHAND
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Dehradun', 'Uttarakhand', 30.316496, 78.032188, 'Dehradun, Uttarakhand'),
('Haridwar', 'Uttarakhand', 29.945270, 78.164227, 'Haridwar, Uttarakhand'),
('Roorkee', 'Uttarakhand', 29.871389, 77.888333, 'Roorkee, Uttarakhand'),
('Haldwani', 'Uttarakhand', 29.219444, 79.520278, 'Haldwani, Uttarakhand'),
('Rudrapur', 'Uttarakhand', 28.975000, 79.400000, 'Rudrapur, Uttarakhand'),
('Kashipur', 'Uttarakhand', 29.213889, 78.960833, 'Kashipur, Uttarakhand'),
('Rishikesh', 'Uttarakhand', 30.087222, 78.267778, 'Rishikesh, Uttarakhand'),
('Pithoragarh', 'Uttarakhand', 29.583333, 80.216667, 'Pithoragarh, Uttarakhand'),
('Ramnagar', 'Uttarakhand', 29.394722, 79.127778, 'Ramnagar, Uttarakhand'),
('Tehri', 'Uttarakhand', 30.391111, 78.480278, 'Tehri, Uttarakhand'),
('Almora', 'Uttarakhand', 29.598611, 79.659722, 'Almora, Uttarakhand'),
('Nainital', 'Uttarakhand', 29.380556, 79.454167, 'Nainital, Uttarakhand'),
('Mussoorie', 'Uttarakhand', 30.455000, 78.079167, 'Mussoorie, Uttarakhand'),
('Srinagar', 'Uttarakhand', 30.221111, 78.780000, 'Srinagar, Uttarakhand'),
('Pauri', 'Uttarakhand', 30.150000, 78.773889, 'Pauri, Uttarakhand'),
('Bageshwar', 'Uttarakhand', 29.838889, 79.771111, 'Bageshwar, Uttarakhand'),
('Champawat', 'Uttarakhand', 29.336667, 80.093889, 'Champawat, Uttarakhand'),
('Jaspur', 'Uttarakhand', 29.283333, 78.827778, 'Jaspur, Uttarakhand'),
('Kotdwar', 'Uttarakhand', 29.746389, 78.525833, 'Kotdwar, Uttarakhand'),
('Manglaur', 'Uttarakhand', 29.794722, 77.874167, 'Manglaur, Uttarakhand');

-- WEST BENGAL
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Kolkata', 'West Bengal', 22.572646, 88.363895, 'Kolkata, West Bengal'),
('Howrah', 'West Bengal', 22.589610, 88.309790, 'Howrah, West Bengal'),
('Durgapur', 'West Bengal', 23.520408, 87.311944, 'Durgapur, West Bengal'),
('Asansol', 'West Bengal', 23.683333, 86.983333, 'Asansol, West Bengal'),
('Siliguri', 'West Bengal', 26.710000, 88.430000, 'Siliguri, West Bengal'),
('Bardhaman', 'West Bengal', 23.255000, 87.856667, 'Bardhaman, West Bengal'),
('Malda', 'West Bengal', 25.010000, 88.140000, 'Malda, West Bengal'),
('Baharampur', 'West Bengal', 24.100000, 88.250000, 'Baharampur, West Bengal'),
('Habra', 'West Bengal', 22.832778, 88.631389, 'Habra, West Bengal'),
('Kharagpur', 'West Bengal', 22.330000, 87.319444, 'Kharagpur, West Bengal'),
('Shantipur', 'West Bengal', 23.255000, 88.433333, 'Shantipur, West Bengal'),
('Dankuni', 'West Bengal', 22.675000, 88.274167, 'Dankuni, West Bengal'),
('Dhulian', 'West Bengal', 24.683333, 87.966667, 'Dhulian, West Bengal'),
('Ranaghat', 'West Bengal', 23.175000, 88.575000, 'Ranaghat, West Bengal'),
('Haldia', 'West Bengal', 22.058611, 88.058889, 'Haldia, West Bengal'),
('Raiganj', 'West Bengal', 25.618889, 88.123889, 'Raiganj, West Bengal'),
('Krishnanagar', 'West Bengal', 23.403611, 88.503056, 'Krishnanagar, West Bengal'),
('Nabadwip', 'West Bengal', 23.407500, 88.366667, 'Nabadwip, West Bengal'),
('Medinipur', 'West Bengal', 22.426667, 87.321667, 'Medinipur, West Bengal'),
('Jalpaiguri', 'West Bengal', 26.524444, 88.719722, 'Jalpaiguri, West Bengal'),
('Balurghat', 'West Bengal', 25.216667, 88.766667, 'Balurghat, West Bengal'),
('Basirhat', 'West Bengal', 22.657222, 88.894167, 'Basirhat, West Bengal'),
('Bankura', 'West Bengal', 23.250000, 87.066667, 'Bankura, West Bengal'),
('Chakdaha', 'West Bengal', 23.080000, 88.516667, 'Chakdaha, West Bengal'),
('Darjeeling', 'West Bengal', 27.041000, 88.266670, 'Darjeeling, West Bengal'),
('Alipurduar', 'West Bengal', 26.491389, 89.529167, 'Alipurduar, West Bengal'),
('Purulia', 'West Bengal', 23.342222, 86.364722, 'Purulia, West Bengal'),
('Jangipur', 'West Bengal', 24.466667, 88.066667, 'Jangipur, West Bengal'),
('Bolpur', 'West Bengal', 23.666667, 87.700000, 'Bolpur, West Bengal'),
('Bangaon', 'West Bengal', 23.075000, 88.823333, 'Bangaon, West Bengal');

-- DELHI (NCT)
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('New Delhi', 'Delhi', 28.613939, 77.209021, 'New Delhi, Delhi'),
('Delhi', 'Delhi', 28.704059, 77.102493, 'Delhi, Delhi'),
('Dwarka', 'Delhi', 28.592225, 77.031891, 'Dwarka, Delhi'),
('Rohini', 'Delhi', 28.742962, 77.068337, 'Rohini, Delhi'),
('Najafgarh', 'Delhi', 28.609231, 76.979791, 'Najafgarh, Delhi'),
('Narela', 'Delhi', 28.853056, 77.091111, 'Narela, Delhi');

-- JAMMU AND KASHMIR
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Srinagar', 'Jammu and Kashmir', 34.083656, 74.797371, 'Srinagar, Jammu and Kashmir'),
('Jammu', 'Jammu and Kashmir', 32.735687, 74.869111, 'Jammu, Jammu and Kashmir'),
('Anantnag', 'Jammu and Kashmir', 33.730958, 75.150993, 'Anantnag, Jammu and Kashmir'),
('Baramulla', 'Jammu and Kashmir', 34.209444, 74.342778, 'Baramulla, Jammu and Kashmir'),
('Sopore', 'Jammu and Kashmir', 34.303056, 74.471111, 'Sopore, Jammu and Kashmir'),
('Kathua', 'Jammu and Kashmir', 32.370000, 75.520000, 'Kathua, Jammu and Kashmir'),
('Udhampur', 'Jammu and Kashmir', 32.916111, 75.141667, 'Udhampur, Jammu and Kashmir'),
('Pulwama', 'Jammu and Kashmir', 33.870833, 74.893611, 'Pulwama, Jammu and Kashmir'),
('Punch', 'Jammu and Kashmir', 33.770833, 74.093056, 'Punch, Jammu and Kashmir'),
('Rajouri', 'Jammu and Kashmir', 33.379444, 74.313056, 'Rajouri, Jammu and Kashmir');

-- LADAKH
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Leh', 'Ladakh', 34.152588, 77.577049, 'Leh, Ladakh'),
('Kargil', 'Ladakh', 34.558056, 76.129167, 'Kargil, Ladakh'),
('Nubra', 'Ladakh', 34.533333, 77.566667, 'Nubra, Ladakh');

-- PUDUCHERRY
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Puducherry', 'Puducherry', 11.934444, 79.829444, 'Puducherry, Puducherry'),
('Karaikal', 'Puducherry', 10.924444, 79.838056, 'Karaikal, Puducherry'),
('Yanam', 'Puducherry', 16.733333, 82.216667, 'Yanam, Puducherry'),
('Mahe', 'Puducherry', 11.700000, 75.533333, 'Mahe, Puducherry');

-- CHANDIGARH (UT)
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Chandigarh', 'Chandigarh', 30.733315, 76.779419, 'Chandigarh, Chandigarh');

-- DADRA AND NAGAR HAVELI AND DAMAN AND DIU
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Daman', 'Dadra and Nagar Haveli and Daman and Diu', 20.414217, 72.832764, 'Daman, Dadra and Nagar Haveli and Daman and Diu'),
('Diu', 'Dadra and Nagar Haveli and Daman and Diu', 20.714722, 70.987778, 'Diu, Dadra and Nagar Haveli and Daman and Diu'),
('Silvassa', 'Dadra and Nagar Haveli and Daman and Diu', 20.273889, 73.016389, 'Silvassa, Dadra and Nagar Haveli and Daman and Diu');

-- LAKSHADWEEP
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Kavaratti', 'Lakshadweep', 10.566667, 72.636111, 'Kavaratti, Lakshadweep'),
('Agatti', 'Lakshadweep', 10.850000, 72.200000, 'Agatti, Lakshadweep'),
('Minicoy', 'Lakshadweep', 8.283333, 73.050000, 'Minicoy, Lakshadweep');

-- ANDAMAN AND NICOBAR ISLANDS
INSERT INTO cities (name, state, latitude, longitude, display_name) VALUES
('Port Blair', 'Andaman and Nicobar Islands', 11.666667, 92.750000, 'Port Blair, Andaman and Nicobar Islands'),
('Diglipur', 'Andaman and Nicobar Islands', 13.250000, 93.000000, 'Diglipur, Andaman and Nicobar Islands'),
('Mayabunder', 'Andaman and Nicobar Islands', 12.900000, 92.900000, 'Mayabunder, Andaman and Nicobar Islands'),
('Rangat', 'Andaman and Nicobar Islands', 12.516667, 92.966667, 'Rangat, Andaman and Nicobar Islands');

-- Create full-text search index for better search performance
CREATE INDEX IF NOT EXISTS idx_cities_search ON cities USING gin(to_tsvector('english', display_name));

-- Add comments
COMMENT ON TABLE cities IS 'Indian cities and towns with geographic coordinates for astrology calculations';
COMMENT ON COLUMN cities.display_name IS 'Format: "City, State" for display and search';
