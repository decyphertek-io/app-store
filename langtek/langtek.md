# LangTek - Spanish Language Learning App

## Overview
LangTek is a comprehensive Spanish language learning application built with Flet. It combines RSS feed reading, translation tools, and interactive learning features to provide an immersive Spanish learning experience through real-world content.

## Core Capabilities

### 📚 **Language Learning**
- **Interactive Translation**: Word-by-word and contextual translation of Spanish content
- **Text-to-Speech**: High-quality Spanish pronunciation using gTTS and pyttsx3
- **Dictionary Management**: Personal dictionary with translation history
- **Sentence Analysis**: Break down complex Spanish sentences for learning

### 📰 **RSS Feed Reading**
- **Spanish News**: Read current Spanish news from RSS feeds
- **Feed Management**: Add, remove, and organize RSS sources
- **Article Extraction**: Clean article content extraction from web pages
- **Caching**: Offline reading with intelligent content caching

### 🎯 **Interactive Learning Features**
- **Interactive Translator**: Real-time translation widget for practice
- **Settings Management**: Customize learning preferences and TTS settings
- **Progress Tracking**: Monitor learning progress and vocabulary growth
- **Multi-language Support**: Support for various Spanish dialects

### 🔊 **Audio Features**
- **Text-to-Speech**: Multiple TTS engines (gTTS, pyttsx3, system TTS)
- **Speech Rate Control**: Adjustable speaking speed for different learning levels
- **Language Variants**: Support for different Spanish accents (es-US, es-ES, etc.)
- **Audio Quality**: High-quality audio output for better learning

## User Interface

### **Main Interface**
- **Feed List**: Scrollable list of Spanish articles with translations
- **Article Detail**: Full article view with translation and audio features
- **Interactive Translator**: Dedicated translation practice widget
- **Settings Panel**: Comprehensive configuration options

### **Navigation Structure**
- **Main Feed**: Spanish RSS articles with translations
- **Interactive Translator**: Practice translation skills
- **Settings**: App configuration and preferences
- **Feed Management**: Manage RSS sources
- **Dictionary**: Personal vocabulary management

### **Visual Design**
- **Dark Theme**: Modern dark UI optimized for reading
- **Mobile-First**: Designed for mobile learning experience
- **Responsive Layout**: Adapts to different screen sizes
- **Clean Typography**: Easy-to-read fonts for language learning

## Technical Architecture

### **Dependencies**
- **Flet Framework**: Modern Python GUI framework
- **feedparser**: RSS feed parsing and processing
- **aiohttp**: Asynchronous HTTP requests for web content
- **beautifulsoup4**: HTML content extraction and cleaning
- **pyttsx3**: Cross-platform text-to-speech
- **gtts**: Google Text-to-Speech for high-quality audio
- **pygame**: Audio playback and multimedia support
- **requests**: HTTP requests for translation services

### **Key Modules**
- `main.py`: Application entry point and main UI
- `article_detail_screen.py`: Full article viewing interface
- `article_extractor.py`: Web content extraction
- `cache_service.py`: Content caching and offline storage
- `dictionary_service.py`: Translation and vocabulary management
- `feed_management_screen.py`: RSS feed configuration
- `interactive_translator_widget.py`: Translation practice tool
- `settings_screen.py`: Application configuration
- `tts_settings_screen.py`: Text-to-speech configuration
- `sentence_widget.py`: Sentence analysis and learning

## Learning Features

### **RSS Feed Integration**
- **Spanish News Sources**: Access to current Spanish news and articles
- **Automatic Translation**: Real-time translation of article titles and content
- **Content Caching**: Offline reading capability
- **Source Management**: Easy addition and removal of RSS feeds

### **Translation Tools**
- **Word-by-Word Translation**: Individual word translations for learning
- **Contextual Translation**: Full sentence and paragraph translations
- **Google Translate Integration**: High-quality translation services
- **Translation History**: Track previously translated content

### **Audio Learning**
- **Multiple TTS Engines**: gTTS, pyttsx3, and system TTS support
- **Speech Rate Control**: Adjustable speed for different learning levels
- **Language Variants**: Support for different Spanish accents
- **Audio Playback**: High-quality audio output

### **Interactive Features**
- **Interactive Translator**: Practice translation skills
- **Dictionary Management**: Personal vocabulary building
- **Settings Customization**: Personalized learning experience
- **Progress Tracking**: Monitor learning achievements

## Usage Patterns

### **For Spanish Learners**
1. **Daily Reading**: Use RSS feeds to read Spanish news daily
2. **Vocabulary Building**: Add new words to personal dictionary
3. **Pronunciation Practice**: Use TTS to learn proper pronunciation
4. **Translation Practice**: Use interactive translator for skill building

### **For Language Teachers**
1. **Content Curation**: Select appropriate RSS sources for students
2. **Lesson Planning**: Use articles as teaching materials
3. **Progress Monitoring**: Track student vocabulary growth
4. **Audio Resources**: Provide pronunciation examples

### **For Language Enthusiasts**
1. **Immersion Learning**: Read authentic Spanish content
2. **Cultural Awareness**: Stay updated with Spanish news and culture
3. **Skill Development**: Practice translation and comprehension
4. **Audio Learning**: Improve listening and pronunciation skills

## Integration Capabilities

### **RSS Feed Sources**
- **Spanish News**: El País, El Mundo, BBC Mundo, etc.
- **Custom Feeds**: Add any Spanish RSS feed
- **Content Filtering**: Filter content by topic or difficulty
- **Offline Reading**: Download articles for offline study

### **Translation Services**
- **Google Translate**: High-quality translation API
- **Local Dictionary**: Personal vocabulary database
- **Translation Caching**: Store translations for offline access
- **Multi-language Support**: Various Spanish dialects

### **Audio Services**
- **gTTS**: Google Text-to-Speech for high-quality audio
- **pyttsx3**: Cross-platform TTS for offline use
- **System TTS**: Native system text-to-speech
- **Audio Caching**: Store audio for offline listening

## Security Features

### **Data Privacy**
- **Local Storage**: All personal data stored locally
- **No Cloud Sync**: Privacy-focused design
- **Encrypted Storage**: Secure local data storage
- **User Control**: Full control over personal information

### **Content Safety**
- **RSS Filtering**: Safe content from trusted sources
- **Content Moderation**: Appropriate content for learning
- **Safe Browsing**: Secure web content extraction
- **Privacy Protection**: No tracking or data collection

## Deployment

### **Standalone Application**
- **PyInstaller Build**: Single executable file (langtek.app)
- **No Dependencies**: Self-contained with all required libraries
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Easy Distribution**: Simple deployment without installation requirements

### **System Requirements**
- **Python**: 3.9+ (for development)
- **Memory**: 256MB+ RAM recommended
- **Storage**: 50MB+ for application and dependencies
- **Network**: Internet access for RSS feeds and translation services
- **Audio**: Sound card for text-to-speech features

## Best Practices

### **Learning Optimization**
1. **Daily Practice**: Regular reading and translation practice
2. **Vocabulary Building**: Consistent dictionary management
3. **Audio Learning**: Regular use of text-to-speech features
4. **Progress Tracking**: Monitor learning achievements

### **Content Management**
1. **Quality Sources**: Use reputable Spanish news sources
2. **Difficulty Progression**: Start with simpler content and progress
3. **Topic Diversity**: Read about various subjects
4. **Regular Updates**: Keep RSS feeds current and relevant

### **Technical Considerations**
1. **Offline Learning**: Download content for offline study
2. **Audio Quality**: Use high-quality TTS for better learning
3. **Storage Management**: Regular cleanup of cached content
4. **Network Usage**: Optimize for mobile data usage

## Troubleshooting

### **Common Issues**
- **RSS Feed Loading**: Check internet connection and feed URLs
- **Translation Services**: Verify internet connectivity for Google Translate
- **Audio Playback**: Check audio drivers and TTS engine installation
- **Content Extraction**: Ensure web content is accessible

### **Support Resources**
- **Built-in Help**: Integrated documentation and user guide
- **Settings Panel**: Comprehensive configuration options
- **Error Logging**: Detailed logging for debugging
- **Community Support**: Access to user community and documentation

## Learning Methodology

### **Immersive Learning**
- **Real Content**: Learn from authentic Spanish news and articles
- **Contextual Learning**: Understand words in real-world contexts
- **Cultural Awareness**: Learn about Spanish-speaking cultures
- **Current Events**: Stay updated with Spanish news and events

### **Progressive Learning**
- **Beginner Level**: Start with simple articles and basic vocabulary
- **Intermediate Level**: Progress to more complex content
- **Advanced Level**: Challenge with technical and specialized content
- **Continuous Improvement**: Regular practice and vocabulary expansion
