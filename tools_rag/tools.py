"""Tool catalogue for RAG system, organized by MCP server."""

# ==============================================================================
# WEATHER & ENVIRONMENT - weather-mcp
# ==============================================================================
weather_tools = [
    {
        "name": "get_weather",
        "desc": "Current weather for a city",
        "params": {"city": {"type": "string"}},
        "server": "weather-mcp",
    },
    {
        "name": "get_forecast",
        "desc": "Get weather forecast for next 7 days",
        "params": {"location": {"type": "string"}},
        "server": "weather-mcp",
    },
    {
        "name": "check_air_quality",
        "desc": "Check air quality index and pollution levels",
        "params": {"city": {"type": "string"}},
        "server": "weather-mcp",
    },
]

# ==============================================================================
# NEWS & INFORMATION - news-mcp
# ==============================================================================
news_tools = [
    {
        "name": "get_news",
        "desc": "Latest news headlines",
        "params": {"category": {"type": "string", "enum": ["sport", "tech"]}},
        "server": "news-mcp",
    },
    {
        "name": "search_articles",
        "desc": "Search news articles by keyword",
        "params": {"keyword": {"type": "string"}},
        "server": "news-mcp",
    },
    {
        "name": "get_trending",
        "desc": "Get trending topics on social media",
        "params": {"platform": {"type": "string"}},
        "server": "news-mcp",
    },
]

# ==============================================================================
# KNOWLEDGE & SEARCH - wikipedia-mcp
# ==============================================================================
knowledge_tools = [
    {
        "name": "search_wiki",
        "desc": "Search Wikipedia articles",
        "params": {"query": {"type": "string"}},
        "server": "wikipedia-mcp",
    },
]

# ==============================================================================
# HEALTH & FITNESS - health-mcp
# ==============================================================================
health_tools = [
    {
        "name": "calc_bmi",
        "desc": "Compute BMI",
        "params": {"weight": {"type": "number"}, "height": {"type": "number"}},
        "server": "health-mcp",
    },
    {
        "name": "track_calories",
        "desc": "Track calorie intake for food",
        "params": {"food": {"type": "string"}, "serving": {"type": "number"}},
        "server": "health-mcp",
    },
    {
        "name": "log_workout",
        "desc": "Log exercise and fitness activity",
        "params": {"activity": {"type": "string"}, "duration": {"type": "number"}},
        "server": "health-mcp",
    },
    {
        "name": "get_health_tips",
        "desc": "Get health and wellness recommendations",
        "params": {"topic": {"type": "string"}},
        "server": "health-mcp",
    },
]

# ==============================================================================
# COMMUNICATION - communication-mcp
# ==============================================================================
communication_tools = [
    {
        "name": "translate",
        "desc": "Translate text",
        "params": {"text": {"type": "string"}, "target_lang": {"type": "string"}},
        "server": "communication-mcp",
    },
    {
        "name": "send_email",
        "desc": "Compose and send email to people",
        "params": {
            "to": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"},
        },
        "server": "communication-mcp",
    },
    {
        "name": "send_sms",
        "desc": "Send SMS text message",
        "params": {"phone": {"type": "string"}, "message": {"type": "string"}},
        "server": "communication-mcp",
    },
    {
        "name": "grammar_check",
        "desc": "Check grammar and spelling in text",
        "params": {"text": {"type": "string"}},
        "server": "communication-mcp",
    },
]

# ==============================================================================
# DATA & VISUALIZATION - analytics-mcp
# ==============================================================================
analytics_tools = [
    {
        "name": "plot_chart",
        "desc": "Generate a line chart from CSV",
        "params": {"csv_path": {"type": "string"}},
        "server": "analytics-mcp",
    },
    {
        "name": "create_bar_chart",
        "desc": "Create bar chart from data",
        "params": {"data": {"type": "array"}, "labels": {"type": "array"}},
        "server": "analytics-mcp",
    },
    {
        "name": "generate_report",
        "desc": "Generate PDF report from data",
        "params": {"data_source": {"type": "string"}, "template": {"type": "string"}},
        "server": "analytics-mcp",
    },
    {
        "name": "export_csv",
        "desc": "Export data to CSV file",
        "params": {"data": {"type": "array"}, "filename": {"type": "string"}},
        "server": "analytics-mcp",
    },
]

# ==============================================================================
# TRAVEL & TRANSPORTATION - travel-mcp
# ==============================================================================
travel_tools = [
    {
        "name": "search_flights",
        "desc": "Find available flights between airports",
        "params": {
            "from": {"type": "string"},
            "to": {"type": "string"},
            "date": {"type": "string"},
        },
        "server": "travel-mcp",
    },
    {
        "name": "book_hotel",
        "desc": "Search and book hotel rooms",
        "params": {
            "city": {"type": "string"},
            "checkin": {"type": "string"},
            "checkout": {"type": "string"},
        },
        "server": "travel-mcp",
    },
    {
        "name": "get_directions",
        "desc": "Get driving directions between locations",
        "params": {"from": {"type": "string"}, "to": {"type": "string"}},
        "server": "travel-mcp",
    },
    {
        "name": "check_traffic",
        "desc": "Check traffic conditions on route",
        "params": {"route": {"type": "string"}},
        "server": "travel-mcp",
    },
    {
        "name": "find_parking",
        "desc": "Find nearby parking spots",
        "params": {"location": {"type": "string"}},
        "server": "travel-mcp",
    },
]

# ==============================================================================
# FINANCE & MONEY - finance-mcp
# ==============================================================================
finance_tools = [
    {
        "name": "get_stock_price",
        "desc": "Get current stock price and market data",
        "params": {"symbol": {"type": "string"}},
        "server": "finance-mcp",
    },
    {
        "name": "convert_currency",
        "desc": "Convert amount between currencies",
        "params": {
            "amount": {"type": "number"},
            "from_currency": {"type": "string"},
            "to_currency": {"type": "string"},
        },
        "server": "finance-mcp",
    },
    {
        "name": "track_expenses",
        "desc": "Track and categorize expenses",
        "params": {"amount": {"type": "number"}, "category": {"type": "string"}},
        "server": "finance-mcp",
    },
    {
        "name": "get_crypto_price",
        "desc": "Get cryptocurrency prices and market cap",
        "params": {"symbol": {"type": "string"}},
        "server": "finance-mcp",
    },
    {
        "name": "calculate_tax",
        "desc": "Calculate tax amount for income",
        "params": {"income": {"type": "number"}, "tax_rate": {"type": "number"}},
        "server": "finance-mcp",
    },
]

# ==============================================================================
# TIME & PRODUCTIVITY - productivity-mcp
# ==============================================================================
productivity_tools = [
    {
        "name": "get_time",
        "desc": "Get current time in timezone",
        "params": {"timezone": {"type": "string"}},
        "server": "productivity-mcp",
    },
    {
        "name": "set_reminder",
        "desc": "Set a reminder for specific time",
        "params": {"message": {"type": "string"}, "datetime": {"type": "string"}},
        "server": "productivity-mcp",
    },
    {
        "name": "create_calendar_event",
        "desc": "Create event in calendar",
        "params": {
            "title": {"type": "string"},
            "datetime": {"type": "string"},
            "duration": {"type": "number"},
        },
        "server": "productivity-mcp",
    },
    {
        "name": "set_timer",
        "desc": "Set countdown timer",
        "params": {"duration": {"type": "number"}, "label": {"type": "string"}},
        "server": "productivity-mcp",
    },
    {
        "name": "get_calendar",
        "desc": "Get calendar events, schedule, or agenda for date range",
        "params": {"start_date": {"type": "string"}, "end_date": {"type": "string"}},
        "server": "productivity-mcp",
    },
]

# ==============================================================================
# MATH & CALCULATIONS - calculator-mcp
# ==============================================================================
calculator_tools = [
    {
        "name": "calculate",
        "desc": "Evaluate mathematical expression",
        "params": {"expression": {"type": "string"}},
        "server": "calculator-mcp",
    },
    {
        "name": "solve_equation",
        "desc": "Solve algebraic equations",
        "params": {"equation": {"type": "string"}},
        "server": "calculator-mcp",
    },
    {
        "name": "convert_units",
        "desc": "Convert between measurement units",
        "params": {
            "value": {"type": "number"},
            "from_unit": {"type": "string"},
            "to_unit": {"type": "string"},
        },
        "server": "calculator-mcp",
    },
]

# ==============================================================================
# FOOD & DINING - food-mcp
# ==============================================================================
food_tools = [
    {
        "name": "book_restaurant",
        "desc": "Reserve table at restaurant",
        "params": {
            "restaurant": {"type": "string"},
            "people": {"type": "number"},
            "datetime": {"type": "string"},
        },
        "server": "food-mcp",
    },
    {
        "name": "search_recipes",
        "desc": "Find cooking recipes by ingredients or cuisine",
        "params": {"query": {"type": "string"}},
        "server": "food-mcp",
    },
    {
        "name": "order_food",
        "desc": "Order food delivery from restaurants",
        "params": {"restaurant": {"type": "string"}, "items": {"type": "array"}},
        "server": "food-mcp",
    },
    {
        "name": "find_restaurants",
        "desc": "Find nearby restaurants by cuisine",
        "params": {"cuisine": {"type": "string"}, "location": {"type": "string"}},
        "server": "food-mcp",
    },
]

# ==============================================================================
# ENTERTAINMENT & MEDIA - entertainment-mcp
# ==============================================================================
entertainment_tools = [
    {
        "name": "search_movies",
        "desc": "Search for movies and showtimes",
        "params": {"title": {"type": "string"}, "location": {"type": "string"}},
        "server": "entertainment-mcp",
    },
    {
        "name": "get_book_info",
        "desc": "Get information about books",
        "params": {"title": {"type": "string"}},
        "server": "entertainment-mcp",
    },
    {
        "name": "search_music",
        "desc": "Search for songs and artists",
        "params": {"query": {"type": "string"}},
        "server": "entertainment-mcp",
    },
]

# ==============================================================================
# SMART HOME & IoT - smarthome-mcp
# ==============================================================================
smarthome_tools = [
    {
        "name": "control_lights",
        "desc": "Control smart home lights",
        "params": {
            "room": {"type": "string"},
            "action": {"type": "string", "enum": ["on", "off", "dim"]},
        },
        "server": "smarthome-mcp",
    },
    {
        "name": "set_thermostat",
        "desc": "Set home temperature",
        "params": {"temperature": {"type": "number"}, "unit": {"type": "string"}},
        "server": "smarthome-mcp",
    },
]

# ==============================================================================
# SHOPPING & E-COMMERCE - shopping-mcp
# ==============================================================================
shopping_tools = [
    {
        "name": "search_products",
        "desc": "Search for products online",
        "params": {"query": {"type": "string"}, "category": {"type": "string"}},
        "server": "shopping-mcp",
    },
    {
        "name": "track_package",
        "desc": "Track shipping package status",
        "params": {"tracking_number": {"type": "string"}},
        "server": "shopping-mcp",
    },
    {
        "name": "compare_prices",
        "desc": "Compare prices across online stores",
        "params": {"product": {"type": "string"}},
        "server": "shopping-mcp",
    },
    {
        "name": "add_to_cart",
        "desc": "Add item to shopping cart",
        "params": {"product_id": {"type": "string"}, "quantity": {"type": "number"}},
        "server": "shopping-mcp",
    },
    {
        "name": "apply_coupon",
        "desc": "Apply discount coupon code",
        "params": {"code": {"type": "string"}},
        "server": "shopping-mcp",
    },
    {
        "name": "check_inventory",
        "desc": "Check product stock availability",
        "params": {"product_id": {"type": "string"}, "store": {"type": "string"}},
        "server": "shopping-mcp",
    },
    {
        "name": "create_wishlist",
        "desc": "Create or update shopping wishlist",
        "params": {"items": {"type": "array"}},
        "server": "shopping-mcp",
    },
]

# ==============================================================================
# SOCIAL MEDIA & NETWORKING - social-mcp
# ==============================================================================
social_tools = [
    {
        "name": "post_tweet",
        "desc": "Post message on Twitter",
        "params": {"message": {"type": "string"}},
        "server": "social-mcp",
    },
    {
        "name": "share_facebook",
        "desc": "Share content on Facebook",
        "params": {"content": {"type": "string"}, "visibility": {"type": "string"}},
        "server": "social-mcp",
    },
    {
        "name": "send_linkedin_message",
        "desc": "Send direct message on LinkedIn",
        "params": {"recipient": {"type": "string"}, "message": {"type": "string"}},
        "server": "social-mcp",
    },
    {
        "name": "post_instagram",
        "desc": "Post photo to Instagram",
        "params": {"image_url": {"type": "string"}, "caption": {"type": "string"}},
        "server": "social-mcp",
    },
    {
        "name": "schedule_social_post",
        "desc": "Schedule social media post for later",
        "params": {
            "platform": {"type": "string"},
            "content": {"type": "string"},
            "datetime": {"type": "string"},
        },
        "server": "social-mcp",
    },
]

# ==============================================================================
# DOCUMENT & FILE MANAGEMENT - documents-mcp
# ==============================================================================
document_tools = [
    {
        "name": "create_document",
        "desc": "Create new text document",
        "params": {"title": {"type": "string"}, "content": {"type": "string"}},
        "server": "documents-mcp",
    },
    {
        "name": "convert_pdf",
        "desc": "Convert document to PDF format",
        "params": {"file_path": {"type": "string"}},
        "server": "documents-mcp",
    },
    {
        "name": "merge_pdfs",
        "desc": "Merge multiple PDF files into one",
        "params": {"pdf_files": {"type": "array"}},
        "server": "documents-mcp",
    },
    {
        "name": "compress_file",
        "desc": "Compress file or folder to zip",
        "params": {"path": {"type": "string"}},
        "server": "documents-mcp",
    },
    {
        "name": "extract_text",
        "desc": "Extract text from PDF or image",
        "params": {"file_path": {"type": "string"}},
        "server": "documents-mcp",
    },
    {
        "name": "scan_document",
        "desc": "Scan paper document to digital",
        "params": {"output_format": {"type": "string"}},
        "server": "documents-mcp",
    },
]

# ==============================================================================
# CODE & DEVELOPMENT - devtools-mcp
# ==============================================================================
devtools_tools = [
    {
        "name": "format_code",
        "desc": "Format and beautify source code",
        "params": {"code": {"type": "string"}, "language": {"type": "string"}},
        "server": "devtools-mcp",
    },
    {
        "name": "run_tests",
        "desc": "Execute unit tests for code",
        "params": {"test_suite": {"type": "string"}},
        "server": "devtools-mcp",
    },
    {
        "name": "git_commit",
        "desc": "Create git commit with message",
        "params": {"message": {"type": "string"}, "files": {"type": "array"}},
        "server": "devtools-mcp",
    },
    {
        "name": "deploy_app",
        "desc": "Deploy application to server",
        "params": {"environment": {"type": "string"}},
        "server": "devtools-mcp",
    },
    {
        "name": "check_syntax",
        "desc": "Check code syntax for errors",
        "params": {"code": {"type": "string"}, "language": {"type": "string"}},
        "server": "devtools-mcp",
    },
]

# ==============================================================================
# LEARNING & EDUCATION - education-mcp
# ==============================================================================
education_tools = [
    {
        "name": "search_courses",
        "desc": "Find online courses and tutorials",
        "params": {"topic": {"type": "string"}},
        "server": "education-mcp",
    },
    {
        "name": "translate_language",
        "desc": "Learn word translations and definitions",
        "params": {"word": {"type": "string"}, "language": {"type": "string"}},
        "server": "education-mcp",
    },
    {
        "name": "create_flashcards",
        "desc": "Create study flashcards",
        "params": {"topic": {"type": "string"}, "cards": {"type": "array"}},
        "server": "education-mcp",
    },
    {
        "name": "take_quiz",
        "desc": "Take educational quiz on topic",
        "params": {"subject": {"type": "string"}, "difficulty": {"type": "string"}},
        "server": "education-mcp",
    },
    {
        "name": "get_homework_help",
        "desc": "Get help with homework problems",
        "params": {"subject": {"type": "string"}, "question": {"type": "string"}},
        "server": "education-mcp",
    },
]

# ==============================================================================
# SECURITY & PRIVACY - security-mcp
# ==============================================================================
security_tools = [
    {
        "name": "generate_password",
        "desc": "Generate secure random password",
        "params": {
            "length": {"type": "number"},
            "include_symbols": {"type": "boolean"},
        },
        "server": "security-mcp",
    },
    {
        "name": "check_password_strength",
        "desc": "Check password security strength",
        "params": {"password": {"type": "string"}},
        "server": "security-mcp",
    },
    {
        "name": "encrypt_file",
        "desc": "Encrypt file with password",
        "params": {"file_path": {"type": "string"}, "password": {"type": "string"}},
        "server": "security-mcp",
    },
    {
        "name": "scan_virus",
        "desc": "Scan file for viruses and malware",
        "params": {"file_path": {"type": "string"}},
        "server": "security-mcp",
    },
    {
        "name": "enable_2fa",
        "desc": "Enable two-factor authentication",
        "params": {"account": {"type": "string"}, "method": {"type": "string"}},
        "server": "security-mcp",
    },
]

# ==============================================================================
# IMAGE & PHOTO EDITING - image-mcp
# ==============================================================================
image_tools = [
    {
        "name": "resize_image",
        "desc": "Resize image dimensions",
        "params": {
            "image_path": {"type": "string"},
            "width": {"type": "number"},
            "height": {"type": "number"},
        },
        "server": "image-mcp",
    },
    {
        "name": "crop_image",
        "desc": "Crop image to specific area",
        "params": {"image_path": {"type": "string"}, "coordinates": {"type": "object"}},
        "server": "image-mcp",
    },
    {
        "name": "apply_filter",
        "desc": "Apply filter or effect to photo",
        "params": {"image_path": {"type": "string"}, "filter_type": {"type": "string"}},
        "server": "image-mcp",
    },
    {
        "name": "remove_background",
        "desc": "Remove background from image",
        "params": {"image_path": {"type": "string"}},
        "server": "image-mcp",
    },
    {
        "name": "convert_image_format",
        "desc": "Convert image to different format",
        "params": {"image_path": {"type": "string"}, "format": {"type": "string"}},
        "server": "image-mcp",
    },
]

# ==============================================================================
# AUDIO & MUSIC - audio-mcp
# ==============================================================================
audio_tools = [
    {
        "name": "play_music",
        "desc": "Play music track or playlist",
        "params": {"query": {"type": "string"}},
        "server": "audio-mcp",
    },
    {
        "name": "create_playlist",
        "desc": "Create music playlist",
        "params": {"name": {"type": "string"}, "songs": {"type": "array"}},
        "server": "audio-mcp",
    },
    {
        "name": "record_audio",
        "desc": "Record audio from microphone",
        "params": {"duration": {"type": "number"}},
        "server": "audio-mcp",
    },
    {
        "name": "convert_audio_format",
        "desc": "Convert audio file format",
        "params": {"file_path": {"type": "string"}, "format": {"type": "string"}},
        "server": "audio-mcp",
    },
    {
        "name": "get_lyrics",
        "desc": "Get song lyrics by title",
        "params": {"song": {"type": "string"}, "artist": {"type": "string"}},
        "server": "audio-mcp",
    },
]

# ==============================================================================
# VIDEO & STREAMING - video-mcp
# ==============================================================================
video_tools = [
    {
        "name": "download_video",
        "desc": "Download video from URL",
        "params": {"url": {"type": "string"}, "quality": {"type": "string"}},
        "server": "video-mcp",
    },
    {
        "name": "trim_video",
        "desc": "Trim video to specific duration",
        "params": {
            "video_path": {"type": "string"},
            "start_time": {"type": "number"},
            "end_time": {"type": "number"},
        },
        "server": "video-mcp",
    },
    {
        "name": "add_subtitles",
        "desc": "Add subtitles to video",
        "params": {
            "video_path": {"type": "string"},
            "subtitle_file": {"type": "string"},
        },
        "server": "video-mcp",
    },
    {
        "name": "stream_video",
        "desc": "Stream video to TV or device",
        "params": {"video_path": {"type": "string"}, "device": {"type": "string"}},
        "server": "video-mcp",
    },
]

# ==============================================================================
# MAPS & LOCATION - maps-mcp
# ==============================================================================
maps_tools = [
    {
        "name": "find_nearby",
        "desc": "Find nearby points of interest",
        "params": {"type": {"type": "string"}, "location": {"type": "string"}},
        "server": "maps-mcp",
    },
    {
        "name": "get_coordinates",
        "desc": "Get GPS coordinates of address",
        "params": {"address": {"type": "string"}},
        "server": "maps-mcp",
    },
    {
        "name": "calculate_distance",
        "desc": "Calculate distance between locations",
        "params": {"from": {"type": "string"}, "to": {"type": "string"}},
        "server": "maps-mcp",
    },
    {
        "name": "get_elevation",
        "desc": "Get elevation altitude for location",
        "params": {"location": {"type": "string"}},
        "server": "maps-mcp",
    },
]

# ==============================================================================
# GAMING - gaming-mcp
# ==============================================================================
gaming_tools = [
    {
        "name": "get_game_stats",
        "desc": "Get gaming statistics and scores",
        "params": {"game": {"type": "string"}, "player": {"type": "string"}},
        "server": "gaming-mcp",
    },
    {
        "name": "find_game_servers",
        "desc": "Find online game servers",
        "params": {"game": {"type": "string"}, "region": {"type": "string"}},
        "server": "gaming-mcp",
    },
    {
        "name": "get_game_news",
        "desc": "Get latest gaming news and updates",
        "params": {"game": {"type": "string"}},
        "server": "gaming-mcp",
    },
]

# ==============================================================================
# COMBINED TOOLS LIST
# ==============================================================================
tools = (
    weather_tools
    + news_tools
    + knowledge_tools
    + health_tools
    + communication_tools
    + analytics_tools
    + travel_tools
    + finance_tools
    + productivity_tools
    + calculator_tools
    + food_tools
    + entertainment_tools
    + smarthome_tools
    + shopping_tools
    + social_tools
    + document_tools
    + devtools_tools
    + education_tools
    + security_tools
    + image_tools
    + audio_tools
    + video_tools
    + maps_tools
    + gaming_tools
)
