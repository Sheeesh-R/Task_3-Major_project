CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    short_description TEXT NOT NULL,
    long_description TEXT,
    ingredients_text TEXT,
    directions_text TEXT,
    image_path TEXT,
    image_alt TEXT,
    prep_time TEXT,
    cook_time TEXT,
    difficulty TEXT
);

INSERT INTO recipes (
    name, category, short_description, long_description,
    ingredients_text, directions_text, image_path, image_alt,
    prep_time, cook_time, difficulty
)
VALUES
    (
        'Adobo',
        'Main Course',
        'Soy sauce and vinegar-braised pork or chicken with garlic and bay leaves.',
        'Adobo is a beloved Filipino comfort food that simmers meat in a savoury blend of soy sauce, vinegar, garlic, peppercorns, and bay leaves.',
        '1 kg chicken thighs or pork belly\n1/2 cup soy sauce\n1/3 cup cane vinegar\n6 cloves garlic, minced\n2 bay leaves\n1 tsp whole peppercorns\n1 cup water\nSalt to taste',
        'Combine meat with soy sauce, vinegar, garlic, peppercorns, and bay leaves; marinate for 30 minutes.\nBring to a boil, add water, then simmer covered for 30-40 minutes until tender.\nRemove the lid and continue simmering until the sauce thickens.\nServe hot with steamed rice.',
        'images/about.webp',
        'Bowl of chicken adobo served with rice',
        '15 min',
        '45 min',
        'Easy'
    ),
    (
        'Kare-Kare',
        'Main Course',
        'A rich peanut stew traditionally served with oxtail, vegetables, and bagoong.',
        'Kare-Kare features slow-cooked meat and vegetables in a creamy peanut sauce, often paired with shrimp paste for savoury contrast.',
        '1 kg oxtail or beef shanks\n2 cups water or beef stock\n1/2 cup peanut butter\n1/4 cup toasted ground rice\n1 bunch pechay (bok choy)\n1 medium eggplant, sliced\n1 banana blossom, sliced\n2 tbsp annatto seeds in water\nSalt and pepper to taste',
        'Simmer meat in water or stock until tender, skimming excess fat.\nAdd peanut butter, ground rice, and annatto water; stir until sauce thickens.\nAdd vegetables and cook until tender.\nSeason and serve with shrimp paste.',
        'images/about.webp',
        'Bowl of kare-kare stew with vegetables',
        '25 min',
        '1 hr 30 min',
        'Intermediate'
    ),
    (
        'Lumpia',
        'Street Food',
        'Crispy fried spring rolls filled with savoury pork and vegetables.',
        'Lumpia are crisp Filipino spring rolls packed with seasoned meat and vegetables, perfect as appetisers or party snacks.',
        '1 lb ground pork\n1 cup shredded carrots\n1/2 cup chopped onions\n1 cup finely chopped cabbage\n2 cloves garlic, minced\n1 package lumpia wrappers\nSalt and pepper to taste\nOil for frying',
        'Combine pork, vegetables, and garlic; season with salt and pepper.\nPlace 2 tablespoons of filling on a wrapper, fold sides, and roll tightly.\nFry in hot oil until golden brown, about 3-5 minutes.\nDrain on paper towels and serve with sweet and sour sauce.',
        'images/lumpia.jpg',
        'Plate of golden fried lumpia with dipping sauce',
        '30 min',
        '15 min',
        'Medium'
    );
