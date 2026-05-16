"""
Recipe Generator Module
Downloads and uses Kaggle recipe dataset to generate recipes based on detected vegetables.
"""

import os
import json
import pandas as pd
import kagglehub
import threading


# Path to store the downloaded dataset
DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DATASET_READY = False
DATASET_LOCK = threading.Lock()
recipes_df = None

# Fallback recipes in case Kaggle download fails
FALLBACK_RECIPES = {
    'Tomatoes': [
        {
            'name': 'Classic Margherita Pizza',
            'ingredients': ['Fresh tomatoes', 'Mozzarella cheese', 'Fresh basil', 'Olive oil', 'Pizza dough', 'Salt', 'Pepper'],
            'instructions': [
                'Slice fresh tomatoes and arrange on stretched pizza dough.',
                'Tear mozzarella and scatter over tomatoes.',
                'Drizzle with olive oil, season with salt and pepper.',
                'Bake at 250°C for 10-12 minutes until crust is golden.',
                'Top with fresh basil leaves and serve immediately.'
            ],
            'prep_time': '15 min',
            'cook_time': '12 min',
            'servings': 4,
            'difficulty': 'Easy'
        },
        {
            'name': 'Tomato Basil Soup',
            'ingredients': ['Ripe tomatoes', 'Fresh basil', 'Onion', 'Garlic', 'Vegetable broth', 'Heavy cream', 'Olive oil', 'Salt', 'Pepper'],
            'instructions': [
                'Roughly chop tomatoes, onion, and garlic.',
                'Saute onion and garlic in olive oil until soft.',
                'Add tomatoes and broth, simmer for 20 minutes.',
                'Blend until smooth using an immersion blender.',
                'Stir in cream and fresh basil, season to taste.'
            ],
            'prep_time': '10 min',
            'cook_time': '25 min',
            'servings': 4,
            'difficulty': 'Easy'
        },
        {
            'name': 'Fresh Tomato Salsa',
            'ingredients': ['Diced tomatoes', 'Red onion', 'Jalapeno', 'Cilantro', 'Lime juice', 'Salt'],
            'instructions': [
                'Dice tomatoes and red onion finely.',
                'Mince jalapeno, removing seeds for less heat.',
                'Combine all ingredients in a bowl.',
                'Squeeze fresh lime juice over the mixture.',
                'Season with salt and refrigerate for 30 minutes before serving.'
            ],
            'prep_time': '15 min',
            'cook_time': '0 min',
            'servings': 6,
            'difficulty': 'Easy'
        }
    ],
    'Red Bell Peppers': [
        {
            'name': 'Stuffed Bell Peppers',
            'ingredients': ['Red bell peppers', 'Ground beef', 'Rice', 'Onion', 'Garlic', 'Tomato sauce', 'Cheese', 'Italian seasoning'],
            'instructions': [
                'Cut tops off peppers and remove seeds.',
                'Cook rice according to package directions.',
                'Brown ground beef with onion and garlic.',
                'Mix beef with cooked rice, tomato sauce, and seasoning.',
                'Stuff peppers with mixture, top with cheese.',
                'Bake at 190°C for 25-30 minutes until peppers are tender.'
            ],
            'prep_time': '20 min',
            'cook_time': '30 min',
            'servings': 4,
            'difficulty': 'Medium'
        },
        {
            'name': 'Roasted Red Pepper Hummus',
            'ingredients': ['Roasted red peppers', 'Chickpeas', 'Tahini', 'Garlic', 'Lemon juice', 'Olive oil', 'Cumin', 'Salt'],
            'instructions': [
                'Roast peppers under broiler until charred, then peel.',
                'Drain and rinse chickpeas.',
                'Blend peppers, chickpeas, tahini, garlic, and lemon juice.',
                'Stream in olive oil while blending until smooth.',
                'Season with cumin and salt. Serve with pita bread.'
            ],
            'prep_time': '10 min',
            'cook_time': '15 min',
            'servings': 8,
            'difficulty': 'Easy'
        },
        {
            'name': 'Red Pepper Pasta',
            'ingredients': ['Red bell peppers', 'Penne pasta', 'Garlic', 'Heavy cream', 'Parmesan cheese', 'Red pepper flakes', 'Basil', 'Olive oil'],
            'instructions': [
                'Roast peppers, then puree in a blender.',
                'Cook pasta according to package directions.',
                'Saute garlic in olive oil for 1 minute.',
                'Add pepper puree and cream, simmer for 5 minutes.',
                'Toss with cooked pasta, top with parmesan and basil.'
            ],
            'prep_time': '10 min',
            'cook_time': '20 min',
            'servings': 4,
            'difficulty': 'Easy'
        }
    ],
    'Carrots': [
        {
            'name': 'Honey Glazed Carrots',
            'ingredients': ['Baby carrots', 'Honey', 'Butter', 'Thyme', 'Salt', 'Pepper'],
            'instructions': [
                'Peel and trim carrots, cutting larger ones in half.',
                'Melt butter in a large skillet over medium heat.',
                'Add carrots and cook for 5 minutes, stirring occasionally.',
                'Drizzle honey over carrots and add thyme.',
                'Cook for another 5-7 minutes until tender and glazed.',
                'Season with salt and pepper before serving.'
            ],
            'prep_time': '5 min',
            'cook_time': '12 min',
            'servings': 4,
            'difficulty': 'Easy'
        },
        {
            'name': 'Carrot Ginger Soup',
            'ingredients': ['Carrots', 'Fresh ginger', 'Onion', 'Vegetable broth', 'Coconut milk', 'Garlic', 'Cumin', 'Olive oil'],
            'instructions': [
                'Chop carrots, onion, and mince ginger and garlic.',
                'Saute onion, ginger, and garlic in olive oil.',
                'Add carrots, cumin, and broth. Simmer 20 minutes.',
                'Blend until smooth using an immersion blender.',
                'Stir in coconut milk and adjust seasoning.'
            ],
            'prep_time': '10 min',
            'cook_time': '25 min',
            'servings': 4,
            'difficulty': 'Easy'
        },
        {
            'name': 'Carrot Cake',
            'ingredients': ['Grated carrots', 'Flour', 'Sugar', 'Eggs', 'Vegetable oil', 'Cinnamon', 'Walnuts', 'Cream cheese', 'Vanilla extract'],
            'instructions': [
                'Preheat oven to 175°C and grease a cake pan.',
                'Mix flour, sugar, cinnamon, and baking soda.',
                'Whisk eggs, oil, and vanilla separately.',
                'Combine wet and dry ingredients, fold in carrots and walnuts.',
                'Pour into pan and bake for 35-40 minutes.',
                'Cool completely before frosting with cream cheese icing.'
            ],
            'prep_time': '20 min',
            'cook_time': '40 min',
            'servings': 12,
            'difficulty': 'Medium'
        }
    ],
    'Cucumbers/Zucchini': [
        {
            'name': 'Cucumber Raita',
            'ingredients': ['Cucumber', 'Yogurt', 'Cumin', 'Mint', 'Green chili', 'Salt', 'Black pepper'],
            'instructions': [
                'Grate cucumber and squeeze out excess water.',
                'Whisk yogurt until smooth in a bowl.',
                'Add grated cucumber, cumin, and minced green chili.',
                'Garnish with fresh mint leaves.',
                'Refrigerate for 30 minutes before serving with biryani or paratha.'
            ],
            'prep_time': '10 min',
            'cook_time': '0 min',
            'servings': 4,
            'difficulty': 'Easy'
        },
        {
            'name': 'Zucchini Noodles with Pesto',
            'ingredients': ['Zucchini', 'Fresh basil', 'Pine nuts', 'Parmesan', 'Garlic', 'Olive oil', 'Cherry tomatoes', 'Salt'],
            'instructions': [
                'Spiralize zucchini into noodle shapes.',
                'Blend basil, pine nuts, parmesan, garlic, and olive oil for pesto.',
                'Toss zucchini noodles with pesto until well coated.',
                'Halve cherry tomatoes and add to the noodles.',
                'Top with extra parmesan and serve immediately.'
            ],
            'prep_time': '15 min',
            'cook_time': '0 min',
            'servings': 2,
            'difficulty': 'Easy'
        },
        {
            'name': 'Stuffed Zucchini Boats',
            'ingredients': ['Zucchini', 'Ground turkey', 'Tomato sauce', 'Mozzarella', 'Onion', 'Garlic', 'Italian seasoning', 'Parmesan'],
            'instructions': [
                'Halve zucchini lengthwise and scoop out the center.',
                'Brown ground turkey with onion and garlic.',
                'Stir in tomato sauce and Italian seasoning.',
                'Fill zucchini halves with meat mixture.',
                'Top with mozzarella and parmesan.',
                'Bake at 190°C for 20 minutes until tender.'
            ],
            'prep_time': '15 min',
            'cook_time': '20 min',
            'servings': 4,
            'difficulty': 'Medium'
        }
    ],
    'Leafy Greens': [
        {
            'name': 'Sauteed Garlic Spinach',
            'ingredients': ['Fresh spinach', 'Garlic', 'Olive oil', 'Lemon juice', 'Red pepper flakes', 'Salt', 'Pepper'],
            'instructions': [
                'Wash spinach thoroughly and drain.',
                'Heat olive oil in a large skillet over medium heat.',
                'Add minced garlic and red pepper flakes, cook 30 seconds.',
                'Add spinach in batches, tossing until wilted.',
                'Squeeze lemon juice over spinach and season with salt and pepper.',
                'Serve immediately as a side dish.'
            ],
            'prep_time': '5 min',
            'cook_time': '5 min',
            'servings': 4,
            'difficulty': 'Easy'
        },
        {
            'name': 'Green Smoothie Bowl',
            'ingredients': ['Spinach', 'Banana', 'Mango', 'Almond milk', 'Chia seeds', 'Granola', 'Fresh berries', 'Honey'],
            'instructions': [
                'Blend spinach, banana, mango, and almond milk until smooth.',
                'Pour thick smoothie into a bowl.',
                'Top with chia seeds, granola, and fresh berries.',
                'Drizzle with honey for extra sweetness.',
                'Enjoy immediately for the best texture.'
            ],
            'prep_time': '10 min',
            'cook_time': '0 min',
            'servings': 1,
            'difficulty': 'Easy'
        },
        {
            'name': 'Kale Caesar Salad',
            'ingredients': ['Kale', 'Caesar dressing', 'Parmesan', 'Croutons', 'Anchovy', 'Lemon', 'Garlic', 'Olive oil'],
            'instructions': [
                'Remove kale stems and chop leaves finely.',
                'Massage kale with olive oil and pinch of salt for 2 minutes.',
                'Prepare dressing: blend anchovy, garlic, lemon, and olive oil.',
                'Toss kale with dressing until well coated.',
                'Top with shaved parmesan and croutons.',
                'Serve as a main or side salad.'
            ],
            'prep_time': '15 min',
            'cook_time': '0 min',
            'servings': 4,
            'difficulty': 'Easy'
        }
    ],
    'Broccoli': [
        {
            'name': 'Garlic Roasted Broccoli',
            'ingredients': ['Broccoli florets', 'Garlic', 'Olive oil', 'Lemon zest', 'Red pepper flakes', 'Parmesan', 'Salt', 'Pepper'],
            'instructions': [
                'Preheat oven to 220°C.',
                'Toss broccoli florets with olive oil, minced garlic, and red pepper flakes.',
                'Spread on a baking sheet in a single layer.',
                'Roast for 15-20 minutes until edges are crispy.',
                'Zest lemon over broccoli and sprinkle with parmesan.',
                'Season with salt and pepper and serve hot.'
            ],
            'prep_time': '5 min',
            'cook_time': '20 min',
            'servings': 4,
            'difficulty': 'Easy'
        },
        {
            'name': 'Broccoli Cheddar Soup',
            'ingredients': ['Broccoli', 'Cheddar cheese', 'Onion', 'Garlic', 'Vegetable broth', 'Heavy cream', 'Butter', 'Flour', 'Nutmeg'],
            'instructions': [
                'Saute onion and garlic in butter until soft.',
                'Add flour and cook for 1 minute to make a roux.',
                'Gradually whisk in broth and cream.',
                'Add broccoli florets and simmer for 15 minutes.',
                'Blend half the soup for a creamy texture.',
                'Stir in cheddar until melted, season with nutmeg.'
            ],
            'prep_time': '10 min',
            'cook_time': '25 min',
            'servings': 6,
            'difficulty': 'Medium'
        },
        {
            'name': 'Beef and Broccoli Stir Fry',
            'ingredients': ['Broccoli', 'Beef sirloin', 'Soy sauce', 'Garlic', 'Ginger', 'Brown sugar', 'Cornstarch', 'Sesame oil', 'Rice'],
            'instructions': [
                'Slice beef thinly against the grain.',
                'Marinate beef in soy sauce, ginger, and cornstarch.',
                'Blanch broccoli in boiling water for 2 minutes, drain.',
                'Stir fry beef in hot oil until browned, remove.',
                'Stir fry garlic, add sauce ingredients, return beef and broccoli.',
                'Serve over steamed rice.'
            ],
            'prep_time': '15 min',
            'cook_time': '10 min',
            'servings': 4,
            'difficulty': 'Medium'
        }
    ],
    'Corn': [
        {
            'name': 'Grilled Mexican Street Corn',
            'ingredients': ['Corn on the cob', 'Mayonnaise', 'Cotija cheese', 'Chili powder', 'Lime', 'Cilantro', 'Butter'],
            'instructions': [
                'Grill corn on medium-high heat, turning occasionally, until charred.',
                'Mix mayonnaise with lime juice and chili powder.',
                'Brush grilled corn with the mayonnaise mixture.',
                'Sprinkle generously with crumbled cotija cheese.',
                'Dust with more chili powder and garnish with cilantro.',
                'Serve immediately with lime wedges.'
            ],
            'prep_time': '5 min',
            'cook_time': '15 min',
            'servings': 4,
            'difficulty': 'Easy'
        },
        {
            'name': 'Sweet Corn Chowder',
            'ingredients': ['Corn kernels', 'Potato', 'Onion', 'Celery', 'Bacon', 'Heavy cream', 'Butter', 'Thyme', 'Bay leaf'],
            'instructions': [
                'Cook bacon until crispy, crumble and set aside.',
                'Saute onion and celery in butter with bacon drippings.',
                'Add diced potato, corn, thyme, bay leaf, and broth.',
                'Simmer for 15 minutes until potatoes are tender.',
                'Remove bay leaf, add cream, and partially blend.',
                'Top with crumbled bacon and serve.'
            ],
            'prep_time': '15 min',
            'cook_time': '25 min',
            'servings': 6,
            'difficulty': 'Medium'
        },
        {
            'name': 'Corn Fritters',
            'ingredients': ['Corn kernels', 'Flour', 'Eggs', 'Milk', 'Green onion', 'Jalapeno', 'Cheddar', 'Baking powder', 'Oil'],
            'instructions': [
                'Mix flour, baking powder, and salt in a bowl.',
                'Whisk eggs and milk, combine with dry ingredients.',
                'Fold in corn, green onion, jalapeno, and cheese.',
                'Heat oil in a skillet over medium heat.',
                'Drop spoonfuls of batter and fry until golden on both sides.',
                'Drain on paper towels and serve with sour cream.'
            ],
            'prep_time': '10 min',
            'cook_time': '10 min',
            'servings': 4,
            'difficulty': 'Easy'
        }
    ],
    'Eggplant': [
        {
            'name': 'Eggplant Parmesan',
            'ingredients': ['Eggplant', 'Marinara sauce', 'Mozzarella', 'Parmesan', 'Breadcrumbs', 'Eggs', 'Flour', 'Basil', 'Olive oil'],
            'instructions': [
                'Slice eggplant into 1cm rounds and salt to draw moisture.',
                'Pat dry, then dredge in flour, egg, and breadcrumbs.',
                'Fry in olive oil until golden on both sides.',
                'Layer in a baking dish: sauce, eggplant, mozzarella, parmesan.',
                'Repeat layers and top with remaining cheese.',
                'Bake at 190°C for 25 minutes until bubbly and golden.'
            ],
            'prep_time': '20 min',
            'cook_time': '25 min',
            'servings': 6,
            'difficulty': 'Medium'
        },
        {
            'name': 'Baba Ganoush',
            'ingredients': ['Eggplant', 'Tahini', 'Garlic', 'Lemon juice', 'Olive oil', 'Cumin', 'Parsley', 'Salt', 'Paprika'],
            'instructions': [
                'Roast eggplant over open flame or under broiler until charred.',
                'Let cool, then scoop out the flesh.',
                'Blend eggplant with tahini, garlic, lemon juice, and cumin.',
                'Season with salt and adjust lemon juice to taste.',
                'Spread on a plate, drizzle olive oil, and sprinkle paprika.',
                'Garnish with parsley and serve with warm pita.'
            ],
            'prep_time': '10 min',
            'cook_time': '20 min',
            'servings': 6,
            'difficulty': 'Easy'
        },
        {
            'name': 'Moussaka',
            'ingredients': ['Eggplant', 'Ground lamb', 'Onion', 'Garlic', 'Tomato sauce', 'Cinnamon', 'Bechamel sauce', 'Potato', 'Olive oil', 'Nutmeg'],
            'instructions': [
                'Slice eggplant and potato, brush with oil, and roast.',
                'Brown ground lamb with onion, garlic, and cinnamon.',
                'Add tomato sauce and simmer for 15 minutes.',
                'Layer in baking dish: potato, meat sauce, eggplant.',
                'Top with bechamel sauce and a pinch of nutmeg.',
                'Bake at 180°C for 40 minutes until golden.'
            ],
            'prep_time': '30 min',
            'cook_time': '40 min',
            'servings': 8,
            'difficulty': 'Hard'
        }
    ],
    'Potatoes': [
        {
            'name': 'Crispy Roasted Potatoes',
            'ingredients': ['Baby potatoes', 'Olive oil', 'Rosemary', 'Garlic', 'Salt', 'Pepper', 'Parsley'],
            'instructions': [
                'Preheat oven to 220°C.',
                'Halve baby potatoes and toss with olive oil.',
                'Spread on a baking sheet cut-side down.',
                'Roast for 30-35 minutes until crispy and golden.',
                'Toss with minced garlic and rosemary in the last 5 minutes.',
                'Season generously and garnish with fresh parsley.'
            ],
            'prep_time': '5 min',
            'cook_time': '35 min',
            'servings': 4,
            'difficulty': 'Easy'
        },
        {
            'name': 'Creamy Mashed Potatoes',
            'ingredients': ['Yukon gold potatoes', 'Butter', 'Heavy cream', 'Garlic', 'Salt', 'Pepper', 'Chives'],
            'instructions': [
                'Peel and cube potatoes, place in cold salted water.',
                'Bring to boil and cook until fork-tender, about 15 minutes.',
                'Drain and return to pot. Add butter and cream.',
                'Mash until smooth and creamy.',
                'Season with salt and pepper.',
                'Garnish with chives and an extra pat of butter.'
            ],
            'prep_time': '10 min',
            'cook_time': '20 min',
            'servings': 6,
            'difficulty': 'Easy'
        },
        {
            'name': 'Aloo Gobi',
            'ingredients': ['Potatoes', 'Cauliflower', 'Turmeric', 'Cumin', 'Mustard seeds', 'Onion', 'Tomato', 'Green chili', 'Cilantro', 'Garam masala'],
            'instructions': [
                'Cube potatoes and cut cauliflower into florets.',
                'Heat oil, add mustard seeds and cumin until they pop.',
                'Add onion and cook until golden.',
                'Add turmeric, garam masala, and green chili.',
                'Add potatoes and cauliflower, toss with spices.',
                'Cover and cook on low heat until tender. Garnish with cilantro.'
            ],
            'prep_time': '15 min',
            'cook_time': '25 min',
            'servings': 4,
            'difficulty': 'Medium'
        }
    ],
    'Onions': [
        {
            'name': 'French Onion Soup',
            'ingredients': ['Onions', 'Beef broth', 'Gruyere cheese', 'Butter', 'White wine', 'Baguette', 'Thyme', 'Bay leaf', 'Flour'],
            'instructions': [
                'Slice onions thinly and cook in butter on low heat for 40 minutes.',
                'Sprinkle flour over caramelized onions and stir.',
                'Deglaze with white wine, then add broth, thyme, and bay leaf.',
                'Simmer for 20 minutes, then season to taste.',
                'Ladle into oven-safe bowls, top with baguette slices and cheese.',
                'Broil until cheese is bubbly and golden.'
            ],
            'prep_time': '10 min',
            'cook_time': '70 min',
            'servings': 4,
            'difficulty': 'Medium'
        },
        {
            'name': 'Onion Rings',
            'ingredients': ['Large onions', 'Buttermilk', 'Flour', 'Cornmeal', 'Baking powder', 'Paprika', 'Salt', 'Oil for frying'],
            'instructions': [
                'Slice onions into 1cm rings and separate.',
                'Soak in buttermilk for 30 minutes.',
                'Mix flour, cornmeal, baking powder, paprika, and salt.',
                'Dredge onion rings in the flour mixture.',
                'Deep fry at 180°C until golden brown.',
                'Drain on paper towels and serve hot with dipping sauce.'
            ],
            'prep_time': '35 min',
            'cook_time': '5 min',
            'servings': 4,
            'difficulty': 'Easy'
        },
        {
            'name': 'Caramelized Onion Tart',
            'ingredients': ['Onions', 'Puff pastry', 'Goat cheese', 'Thyme', 'Butter', 'Balsamic vinegar', 'Eggs', 'Cream', 'Salt'],
            'instructions': [
                'Cook sliced onions in butter on low heat for 30 minutes until deep golden.',
                'Add balsamic vinegar and cook until syrupy.',
                'Roll out puff pastry and prick with a fork.',
                'Spread caramelized onions over pastry, leaving a border.',
                'Dot with goat cheese and pour over egg-cream mixture.',
                'Bake at 200°C for 20-25 minutes until puffed and golden.'
            ],
            'prep_time': '15 min',
            'cook_time': '55 min',
            'servings': 6,
            'difficulty': 'Medium'
        }
    ]
}


def download_kaggle_dataset():
    """
    Download the Kaggle recipe dataset.
    Uses kagglehub to download the Food.com Recipes dataset.
    Runs in background thread with graceful error handling.
    """
    global DATASET_READY, recipes_df

    with DATASET_LOCK:
        if DATASET_READY:
            return True

        try:
            print("Downloading Kaggle dataset: Food.com Recipes...")
            # Download the Food.com Recipes and Interactions dataset
            path = kagglehub.dataset_download(
                "shuyangli94/food-com-recipes-and-user-interactions",
            )
            print(f"Dataset downloaded to: {path}")

            # Find the recipes CSV file
            csv_files = []
            for root, dirs, files in os.walk(path):
                for f in files:
                    if f.endswith('.csv') and 'recipe' in f.lower():
                        csv_files.append(os.path.join(root, f))

            if csv_files:
                print(f"Loading recipes from: {csv_files[0]}")
                # Read only first 50000 rows and relevant columns to save memory
                available_cols = pd.read_csv(csv_files[0], nrows=0).columns.tolist()
                wanted_cols = ['name', 'ingredients', 'steps', 'minutes', 'n_steps',
                               'n_ingredients', 'description', 'tags', 'nutrition']
                use_cols = [c for c in wanted_cols if c in available_cols]
                recipes_df = pd.read_csv(csv_files[0], usecols=use_cols, nrows=50000)
                print(f"Loaded {len(recipes_df)} recipes from Kaggle dataset.")
            else:
                print("No recipe CSV found, using fallback recipes.")
                recipes_df = None

            DATASET_READY = True
            return True

        except Exception as e:
            print(f"Kaggle download failed: {e}")
            print("Using built-in fallback recipes instead.")
            recipes_df = None
            DATASET_READY = True
            return True


def generate_recipes(detected_vegetables):
    """
    Generate recipes based on detected vegetables.
    First tries the Kaggle dataset, then falls back to built-in recipes.
    """
    if not detected_vegetables:
        return {'recipes': [], 'source': 'none', 'message': 'No vegetables detected to generate recipes for.'}

    vegetable_names = [v['name'] for v in detected_vegetables]
    recipes = []

    # Try Kaggle dataset first
    if recipes_df is not None and not recipes_df.empty:
        kaggle_recipes = _search_kaggle_recipes(vegetable_names)
        if kaggle_recipes:
            recipes.extend(kaggle_recipes)

    # Add fallback recipes for detected vegetables
    for veg_name in vegetable_names:
        if veg_name in FALLBACK_RECIPES:
            for recipe in FALLBACK_RECIPES[veg_name]:
                recipe_copy = dict(recipe)
                recipe_copy['source_vegetable'] = veg_name
                recipe_copy['source'] = 'curated'
                recipes.append(recipe_copy)

    # If we have Kaggle recipes, mark the source
    source = 'kaggle+curated' if any(r.get('source') == 'kaggle' for r in recipes) else 'curated'

    return {
        'recipes': recipes,
        'source': source,
        'detected_vegetables': vegetable_names,
        'message': f'Found {len(recipes)} recipes using {", ".join(vegetable_names)}'
    }


def _search_kaggle_recipes(vegetable_names, max_results=3):
    """
    Search the Kaggle recipe dataframe for recipes containing the detected vegetables.
    """
    if recipes_df is None or recipes_df.empty:
        return []

    found_recipes = []

    # Create vegetable keyword variations for searching
    veg_keywords = {}
    for veg in vegetable_names:
        keywords = [veg.lower()]
        if 'Tomatoes' in veg:
            keywords.extend(['tomato', 'tomatoes'])
        elif 'Peppers' in veg:
            keywords.extend(['pepper', 'peppers', 'bell pepper'])
        elif 'Cucumber' in veg:
            keywords.extend(['cucumber', 'zucchini', 'courgette'])
        elif 'Leafy' in veg:
            keywords.extend(['spinach', 'kale', 'lettuce', 'greens', 'chard'])
        elif 'Broccoli' in veg:
            keywords.extend(['broccoli', 'brocolli'])
        elif 'Carrots' in veg:
            keywords.extend(['carrot', 'carrots'])
        elif 'Corn' in veg:
            keywords.extend(['corn', 'maize'])
        elif 'Eggplant' in veg:
            keywords.extend(['eggplant', 'aubergine'])
        elif 'Potatoes' in veg:
            keywords.extend(['potato', 'potatoes'])
        elif 'Onions' in veg:
            keywords.extend(['onion', 'onions'])
        veg_keywords[veg] = keywords

    for veg, keywords in veg_keywords.items():
        try:
            # Search in ingredients column
            if 'ingredients' in recipes_df.columns:
                mask = recipes_df['ingredients'].astype(str).str.lower()
                for kw in keywords:
                    matches = recipes_df[mask.str.contains(kw, na=False)].head(max_results)
                    for _, row in matches.iterrows():
                        recipe = {
                            'name': str(row.get('name', 'Unknown Recipe')),
                            'source_vegetable': veg,
                            'source': 'kaggle',
                            'ingredients': str(row.get('ingredients', '')).split(',') if pd.notna(row.get('ingredients')) else [],
                            'instructions': str(row.get('steps', '')).split('.') if pd.notna(row.get('steps')) else ['See full recipe on Food.com'],
                            'prep_time': f"{row.get('minutes', 30)} min" if pd.notna(row.get('minutes')) else '30 min',
                            'cook_time': 'See recipe',
                            'servings': 4,
                            'difficulty': 'Medium'
                        }
                        found_recipes.append(recipe)
                        if len(found_recipes) >= max_results * len(vegetable_names):
                            break
            if len(found_recipes) >= max_results * len(vegetable_names):
                break
        except Exception as e:
            print(f"Error searching Kaggle recipes for {veg}: {e}")
            continue

    return found_recipes


def get_dataset_status():
    """Return the current status of the Kaggle dataset."""
    return {
        'loaded': DATASET_READY,
        'has_kaggle_data': recipes_df is not None and not recipes_df.empty,
        'recipe_count': len(recipes_df) if recipes_df is not None else 0,
        'fallback_count': sum(len(v) for v in FALLBACK_RECIPES.values())
    }
