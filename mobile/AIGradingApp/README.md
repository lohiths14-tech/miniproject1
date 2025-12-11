# AI Grading System - React Native Mobile App

## Overview

React Native mobile application for the AI-Powered Grading System. Provides students and lecturers access to assignments, code submissions, grading, and gamification features on iOS and Android devices.

## Prerequisites

- Node.js >= 18
- React Native CLI
- Xcode (for iOS development)
- Android Studio (for Android development)
- CocoaPods (for iOS)

## Installation

```bash
# Navigate to mobile app directory
cd mobile/AIGradingApp

# Install dependencies
npm install

# iOS only - install pods
cd ios && pod install && cd ..
```

## Running the App

### iOS
```bash
npm run ios
```

### Android
```bash
npm run android
```

### Metro Bundler (Development Server)
```bash
npm start
```

## Project Structure

```
mobile/AIGradingApp/
├── App.js                  # Main application entry
├── src/
│   ├── screens/            # Screen components
│   │   ├── LoginScreen.js
│   │   ├── DashboardScreen.js
│   │   ├── AssignmentsScreen.js
│   │   ├── CodeEditorScreen.js
│   │   ├── SubmissionsScreen.js
│   │   ├── LeaderboardScreen.js
│   │   └── ProfileScreen.js
│   ├── components/         # Reusable components
│   │   ├── CodeEditor.js
│   │   ├── AssignmentCard.js
│   │   ├── ProgressChart.js
│   │   └── AchievementBadge.js
│   ├── navigation/         # Navigation configuration
│   ├── services/          # API and services
│   │   └── api.js         # API client
│   ├── context/           # React Context
│   │   └── AuthContext.js # Authentication state
│   ├── styles/            # Shared styles
│   └── utils/             # Utility functions
├── android/               # Android native code
├── ios/                   # iOS native code
└── package.json           # Dependencies
```

## Features Implemented

### ✅ Authentication
- Login with email/password
- Persistent session storage
- Automatic token refresh

### ✅ Dashboard
- Assignment overview
- Recent submissions
- Performance metrics
- Achievements display

### ✅ Assignments
- List all assignments
- View assignment details
- Deadline tracking
- Status indicators

### ✅ Code Editor
- Syntax highlighting
- Multi-language support (Python, Java, C++, C, JavaScript)
- Test case running
- Real-time feedback

### ✅ Submissions
- Submit code
- View submission history
- Check scores and feedback
- Plagiarism status

### ✅ Gamification
- View leaderboard
- Track achievements
- Points and rankings
- Progress visualization

## Configuration

### API Endpoint

Edit `src/services/api.js` to change the backend URL:

```javascript
const API_BASE_URL = __DEV__
  ? 'http://localhost:5000'  // Development
  : 'https://your-api.com';  // Production
```

### Android Local Development

For Android emulator to connect to local backend:
```javascript
const API_BASE_URL = 'http://10.0.2.2:5000';  // Android emulator
```

### iOS Local Development

For iOS simulator:
```javascript
const API_BASE_URL = 'http://localhost:5000';  // iOS simulator
```

## Building for Production

### iOS
```bash
# Build archive
cd ios
xcodebuild -workspace AIGradingApp.xcworkspace -scheme AIGradingApp -archivePath ./build/AIGradingApp.xcarchive archive

# Or use Xcode GUI:
# Open ios/AIGradingApp.xcworkspace in Xcode
# Product > Archive
```

### Android
```bash
# Generate signed APK
cd android
./gradlew assembleRelease

# APK will be at: android/app/build/outputs/apk/release/app-release.apk
```

## Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

## Troubleshooting

### Metro Bundler Issues
```bash
# Clear cache
npm start -- --reset-cache
```

### iOS Build Issues
```bash
# Clean build
cd ios
rm -rf build
pod deintegrate
pod install
```

### Android Build Issues
```bash
# Clean Gradle
cd android
./gradlew clean
```

## Next Steps

- [ ] Implement code editor with syntax highlighting
- [ ] Add offline mode with local caching
- [ ] Implement push notifications for assignment updates
- [ ] Add biometric authentication
- [ ] Implement dark mode
- [ ] Add accessibility features

## Dependencies

- React Navigation for routing
- Axios for API calls
- AsyncStorage for local storage
- React Native Vector Icons for icons
- React Native Chart Kit for visualizations
- React Native Code Editor for code editing

## Support

For issues or questions, please refer to:
- [React Native Documentation](https://reactnative.dev/)
- [Project Documentation](../../README.md)
