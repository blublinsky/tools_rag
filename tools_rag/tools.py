"""Tool catalogue for RAG system."""

tools = [
    # Weather & Environment
    {
        "name": "get_weather",
        "desc": "Current weather for a city",
        "params": {"city": {"type": "string"}},
    },
    {
        "name": "get_forecast",
        "desc": "Get weather forecast for next 7 days",
        "params": {"location": {"type": "string"}},
    },
    {
        "name": "check_air_quality",
        "desc": "Check air quality index and pollution levels",
        "params": {"city": {"type": "string"}},
    },
    # News & Information
    {
        "name": "get_news",
        "desc": "Latest news headlines",
        "params": {"category": {"type": "string", "enum": ["sport", "tech"]}},
    },
    {
        "name": "search_wiki",
        "desc": "Search Wikipedia articles",
        "params": {"query": {"type": "string"}},
    },
    {
        "name": "get_trending",
        "desc": "Get trending topics on social media",
        "params": {"platform": {"type": "string"}},
    },
    {
        "name": "search_articles",
        "desc": "Search news articles by keyword",
        "params": {"keyword": {"type": "string"}},
    },
    # Health & Fitness
    {
        "name": "calc_bmi",
        "desc": "Compute BMI",
        "params": {"weight": {"type": "number"}, "height": {"type": "number"}},
    },
    {
        "name": "track_calories",
        "desc": "Track calorie intake for food",
        "params": {"food": {"type": "string"}, "serving": {"type": "number"}},
    },
    {
        "name": "log_workout",
        "desc": "Log exercise and fitness activity",
        "params": {"activity": {"type": "string"}, "duration": {"type": "number"}},
    },
    {
        "name": "get_health_tips",
        "desc": "Get health and wellness recommendations",
        "params": {"topic": {"type": "string"}},
    },
    # Language & Communication
    {
        "name": "translate",
        "desc": "Translate text",
        "params": {"text": {"type": "string"}, "target_lang": {"type": "string"}},
    },
    {
        "name": "send_email",
        "desc": "Compose and send email to people",
        "params": {
            "to": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"},
        },
    },
    {
        "name": "send_sms",
        "desc": "Send SMS text message",
        "params": {"phone": {"type": "string"}, "message": {"type": "string"}},
    },
    {
        "name": "grammar_check",
        "desc": "Check grammar and spelling in text",
        "params": {"text": {"type": "string"}},
    },
    # Data & Visualization
    {
        "name": "plot_chart",
        "desc": "Generate a line chart from CSV",
        "params": {"csv_path": {"type": "string"}},
    },
    {
        "name": "create_bar_chart",
        "desc": "Create bar chart from data",
        "params": {"data": {"type": "array"}, "labels": {"type": "array"}},
    },
    {
        "name": "generate_report",
        "desc": "Generate PDF report from data",
        "params": {"data_source": {"type": "string"}, "template": {"type": "string"}},
    },
    {
        "name": "export_csv",
        "desc": "Export data to CSV file",
        "params": {"data": {"type": "array"}, "filename": {"type": "string"}},
    },
    # Travel & Transportation
    {
        "name": "search_flights",
        "desc": "Find available flights between airports",
        "params": {
            "from": {"type": "string"},
            "to": {"type": "string"},
            "date": {"type": "string"},
        },
    },
    {
        "name": "book_hotel",
        "desc": "Search and book hotel rooms",
        "params": {
            "city": {"type": "string"},
            "checkin": {"type": "string"},
            "checkout": {"type": "string"},
        },
    },
    {
        "name": "get_directions",
        "desc": "Get driving directions between locations",
        "params": {"from": {"type": "string"}, "to": {"type": "string"}},
    },
    {
        "name": "check_traffic",
        "desc": "Check traffic conditions on route",
        "params": {"route": {"type": "string"}},
    },
    {
        "name": "find_parking",
        "desc": "Find nearby parking spots",
        "params": {"location": {"type": "string"}},
    },
    # Finance & Money
    {
        "name": "get_stock_price",
        "desc": "Get current stock price and market data",
        "params": {"symbol": {"type": "string"}},
    },
    {
        "name": "convert_currency",
        "desc": "Convert amount between currencies",
        "params": {
            "amount": {"type": "number"},
            "from_currency": {"type": "string"},
            "to_currency": {"type": "string"},
        },
    },
    {
        "name": "track_expenses",
        "desc": "Track and categorize expenses",
        "params": {"amount": {"type": "number"}, "category": {"type": "string"}},
    },
    {
        "name": "get_crypto_price",
        "desc": "Get cryptocurrency prices and market cap",
        "params": {"symbol": {"type": "string"}},
    },
    {
        "name": "calculate_tax",
        "desc": "Calculate tax amount for income",
        "params": {"income": {"type": "number"}, "tax_rate": {"type": "number"}},
    },
    # Time & Productivity
    {
        "name": "get_time",
        "desc": "Get current time in timezone",
        "params": {"timezone": {"type": "string"}},
    },
    {
        "name": "set_reminder",
        "desc": "Set a reminder for specific time",
        "params": {"message": {"type": "string"}, "datetime": {"type": "string"}},
    },
    {
        "name": "create_calendar_event",
        "desc": "Create event in calendar",
        "params": {
            "title": {"type": "string"},
            "datetime": {"type": "string"},
            "duration": {"type": "number"},
        },
    },
    {
        "name": "set_timer",
        "desc": "Set countdown timer",
        "params": {"duration": {"type": "number"}, "label": {"type": "string"}},
    },
    {
        "name": "get_calendar",
        "desc": "Get calendar events, schedule, or agenda for date range",
        "params": {"start_date": {"type": "string"}, "end_date": {"type": "string"}},
    },
    # Math & Calculations
    {
        "name": "calculate",
        "desc": "Evaluate mathematical expression",
        "params": {"expression": {"type": "string"}},
    },
    {
        "name": "solve_equation",
        "desc": "Solve algebraic equations",
        "params": {"equation": {"type": "string"}},
    },
    {
        "name": "convert_units",
        "desc": "Convert between measurement units",
        "params": {
            "value": {"type": "number"},
            "from_unit": {"type": "string"},
            "to_unit": {"type": "string"},
        },
    },
    # Food & Dining
    {
        "name": "book_restaurant",
        "desc": "Reserve table at restaurant",
        "params": {
            "restaurant": {"type": "string"},
            "people": {"type": "number"},
            "datetime": {"type": "string"},
        },
    },
    {
        "name": "search_recipes",
        "desc": "Find cooking recipes by ingredients or cuisine",
        "params": {"query": {"type": "string"}},
    },
    {
        "name": "order_food",
        "desc": "Order food delivery from restaurants",
        "params": {"restaurant": {"type": "string"}, "items": {"type": "array"}},
    },
    {
        "name": "find_restaurants",
        "desc": "Find nearby restaurants by cuisine",
        "params": {"cuisine": {"type": "string"}, "location": {"type": "string"}},
    },
    # Entertainment & Media
    {
        "name": "search_movies",
        "desc": "Search for movies and showtimes",
        "params": {"title": {"type": "string"}, "location": {"type": "string"}},
    },
    {
        "name": "get_book_info",
        "desc": "Get information about books",
        "params": {"title": {"type": "string"}},
    },
    {
        "name": "search_music",
        "desc": "Search for songs and artists",
        "params": {"query": {"type": "string"}},
    },
    # Smart Home & IoT
    {
        "name": "control_lights",
        "desc": "Control smart home lights",
        "params": {
            "room": {"type": "string"},
            "action": {"type": "string", "enum": ["on", "off", "dim"]},
        },
    },
    {
        "name": "set_thermostat",
        "desc": "Set home temperature",
        "params": {"temperature": {"type": "number"}, "unit": {"type": "string"}},
    },
    # Shopping & E-commerce
    {
        "name": "search_products",
        "desc": "Search for products online",
        "params": {"query": {"type": "string"}, "category": {"type": "string"}},
    },
    {
        "name": "track_package",
        "desc": "Track shipping package status",
        "params": {"tracking_number": {"type": "string"}},
    },
    {
        "name": "compare_prices",
        "desc": "Compare prices across online stores",
        "params": {"product": {"type": "string"}},
    },
    {
        "name": "add_to_cart",
        "desc": "Add item to shopping cart",
        "params": {"product_id": {"type": "string"}, "quantity": {"type": "number"}},
    },
    {
        "name": "apply_coupon",
        "desc": "Apply discount coupon code",
        "params": {"code": {"type": "string"}},
    },
    {
        "name": "check_inventory",
        "desc": "Check product stock availability",
        "params": {"product_id": {"type": "string"}, "store": {"type": "string"}},
    },
    {
        "name": "create_wishlist",
        "desc": "Create or update shopping wishlist",
        "params": {"items": {"type": "array"}},
    },
    # Social Media & Networking
    {
        "name": "post_tweet",
        "desc": "Post message on Twitter",
        "params": {"message": {"type": "string"}},
    },
    {
        "name": "share_facebook",
        "desc": "Share content on Facebook",
        "params": {"content": {"type": "string"}, "visibility": {"type": "string"}},
    },
    {
        "name": "send_linkedin_message",
        "desc": "Send direct message on LinkedIn",
        "params": {"recipient": {"type": "string"}, "message": {"type": "string"}},
    },
    {
        "name": "post_instagram",
        "desc": "Post photo to Instagram",
        "params": {"image_url": {"type": "string"}, "caption": {"type": "string"}},
    },
    {
        "name": "schedule_social_post",
        "desc": "Schedule social media post for later",
        "params": {
            "platform": {"type": "string"},
            "content": {"type": "string"},
            "datetime": {"type": "string"},
        },
    },
    # Document & File Management
    {
        "name": "create_document",
        "desc": "Create new text document",
        "params": {"title": {"type": "string"}, "content": {"type": "string"}},
    },
    {
        "name": "convert_pdf",
        "desc": "Convert document to PDF format",
        "params": {"file_path": {"type": "string"}},
    },
    {
        "name": "merge_pdfs",
        "desc": "Merge multiple PDF files into one",
        "params": {"pdf_files": {"type": "array"}},
    },
    {
        "name": "compress_file",
        "desc": "Compress file or folder to zip",
        "params": {"path": {"type": "string"}},
    },
    {
        "name": "extract_text",
        "desc": "Extract text from PDF or image",
        "params": {"file_path": {"type": "string"}},
    },
    {
        "name": "scan_document",
        "desc": "Scan paper document to digital",
        "params": {"output_format": {"type": "string"}},
    },
    # Code & Development
    {
        "name": "format_code",
        "desc": "Format and beautify source code",
        "params": {"code": {"type": "string"}, "language": {"type": "string"}},
    },
    {
        "name": "run_tests",
        "desc": "Execute unit tests for code",
        "params": {"test_suite": {"type": "string"}},
    },
    {
        "name": "git_commit",
        "desc": "Create git commit with message",
        "params": {"message": {"type": "string"}, "files": {"type": "array"}},
    },
    {
        "name": "deploy_app",
        "desc": "Deploy application to server",
        "params": {"environment": {"type": "string"}},
    },
    {
        "name": "check_syntax",
        "desc": "Check code syntax for errors",
        "params": {"code": {"type": "string"}, "language": {"type": "string"}},
    },
    # Learning & Education
    {
        "name": "search_courses",
        "desc": "Find online courses and tutorials",
        "params": {"topic": {"type": "string"}},
    },
    {
        "name": "translate_language",
        "desc": "Learn word translations and definitions",
        "params": {"word": {"type": "string"}, "language": {"type": "string"}},
    },
    {
        "name": "create_flashcards",
        "desc": "Create study flashcards",
        "params": {"topic": {"type": "string"}, "cards": {"type": "array"}},
    },
    {
        "name": "take_quiz",
        "desc": "Take educational quiz on topic",
        "params": {"subject": {"type": "string"}, "difficulty": {"type": "string"}},
    },
    {
        "name": "get_homework_help",
        "desc": "Get help with homework problems",
        "params": {"subject": {"type": "string"}, "question": {"type": "string"}},
    },
    # Security & Privacy
    {
        "name": "generate_password",
        "desc": "Generate secure random password",
        "params": {
            "length": {"type": "number"},
            "include_symbols": {"type": "boolean"},
        },
    },
    {
        "name": "check_password_strength",
        "desc": "Check password security strength",
        "params": {"password": {"type": "string"}},
    },
    {
        "name": "encrypt_file",
        "desc": "Encrypt file with password",
        "params": {"file_path": {"type": "string"}, "password": {"type": "string"}},
    },
    {
        "name": "scan_virus",
        "desc": "Scan file for viruses and malware",
        "params": {"file_path": {"type": "string"}},
    },
    {
        "name": "enable_2fa",
        "desc": "Enable two-factor authentication",
        "params": {"account": {"type": "string"}, "method": {"type": "string"}},
    },
    # Image & Photo Editing
    {
        "name": "resize_image",
        "desc": "Resize image dimensions",
        "params": {
            "image_path": {"type": "string"},
            "width": {"type": "number"},
            "height": {"type": "number"},
        },
    },
    {
        "name": "crop_image",
        "desc": "Crop image to specific area",
        "params": {"image_path": {"type": "string"}, "coordinates": {"type": "object"}},
    },
    {
        "name": "apply_filter",
        "desc": "Apply filter or effect to photo",
        "params": {"image_path": {"type": "string"}, "filter_type": {"type": "string"}},
    },
    {
        "name": "remove_background",
        "desc": "Remove background from image",
        "params": {"image_path": {"type": "string"}},
    },
    {
        "name": "convert_image_format",
        "desc": "Convert image to different format",
        "params": {"image_path": {"type": "string"}, "format": {"type": "string"}},
    },
    # Audio & Music
    {
        "name": "play_music",
        "desc": "Play music track or playlist",
        "params": {"query": {"type": "string"}},
    },
    {
        "name": "create_playlist",
        "desc": "Create music playlist",
        "params": {"name": {"type": "string"}, "songs": {"type": "array"}},
    },
    {
        "name": "record_audio",
        "desc": "Record audio from microphone",
        "params": {"duration": {"type": "number"}},
    },
    {
        "name": "convert_audio_format",
        "desc": "Convert audio file format",
        "params": {"file_path": {"type": "string"}, "format": {"type": "string"}},
    },
    {
        "name": "get_lyrics",
        "desc": "Get song lyrics by title",
        "params": {"song": {"type": "string"}, "artist": {"type": "string"}},
    },
    # Video & Streaming
    {
        "name": "download_video",
        "desc": "Download video from URL",
        "params": {"url": {"type": "string"}, "quality": {"type": "string"}},
    },
    {
        "name": "trim_video",
        "desc": "Trim video to specific duration",
        "params": {
            "video_path": {"type": "string"},
            "start_time": {"type": "number"},
            "end_time": {"type": "number"},
        },
    },
    {
        "name": "add_subtitles",
        "desc": "Add subtitles to video",
        "params": {
            "video_path": {"type": "string"},
            "subtitle_file": {"type": "string"},
        },
    },
    {
        "name": "stream_video",
        "desc": "Stream video to TV or device",
        "params": {"video_path": {"type": "string"}, "device": {"type": "string"}},
    },
    # Maps & Location
    {
        "name": "find_nearby",
        "desc": "Find nearby points of interest",
        "params": {"type": {"type": "string"}, "location": {"type": "string"}},
    },
    {
        "name": "get_coordinates",
        "desc": "Get GPS coordinates of address",
        "params": {"address": {"type": "string"}},
    },
    {
        "name": "calculate_distance",
        "desc": "Calculate distance between locations",
        "params": {"from": {"type": "string"}, "to": {"type": "string"}},
    },
    {
        "name": "get_elevation",
        "desc": "Get elevation altitude for location",
        "params": {"location": {"type": "string"}},
    },
    # Gaming
    {
        "name": "get_game_stats",
        "desc": "Get gaming statistics and scores",
        "params": {"game": {"type": "string"}, "player": {"type": "string"}},
    },
    {
        "name": "find_game_servers",
        "desc": "Find online game servers",
        "params": {"game": {"type": "string"}, "region": {"type": "string"}},
    },
    {
        "name": "get_game_news",
        "desc": "Get latest gaming news and updates",
        "params": {"game": {"type": "string"}},
    },
]
