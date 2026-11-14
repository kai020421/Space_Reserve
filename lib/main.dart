import 'package:flutter/material.dart';
import 'student_login.dart';
import 'faculty_admin_screen.dart';
import 'faculty_dashboard.dart';
import 'admin_dashboard.dart';

void main() {
  runApp(const SpaceReserveApp());
}

class SpaceReserveApp extends StatelessWidget {
  const SpaceReserveApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SpaceReserve - IBA Karachi',
      debugShowCheckedModeBanner: false,
      themeMode: ThemeMode.dark,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0A0A0A), // Deep Black
        primaryColor: const Color(0xFF990000), // IBA Crimson Red
      ),
      home: const MainLoginContainer(),
      // Named routes for clean logout / navigation redirects (SCRUM-15)
      routes: {
        '/login': (context) => const MainLoginContainer(),
      },
    );
  }
}

class MainLoginContainer extends StatefulWidget {
  const MainLoginContainer({Key? key}) : super(key: key);

  @override
  State<MainLoginContainer> createState() => _MainLoginContainerState();
}

class _MainLoginContainerState extends State<MainLoginContainer> {
  // 0 -> Student Login, 1 -> Faculty / Admin Login
  int _selectedRoleIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Top IBA Logo & Branding Header
                  Center(
                    child: Column(
                      children: [
                        Container(
                          height: 65,
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(12),
                            boxShadow: [
                              BoxShadow(
                                color: const Color(0xFF990000).withOpacity(0.3),
                                blurRadius: 15,
                                offset: const Offset(0, 5),
                              ),
                            ],
                          ),
                          child: Image.asset(
                            'assets/IBA (1).jpeg',
                            fit: BoxFit.contain,
                            errorBuilder: (context, error, stackTrace) => const Text(
                              'IBA Karachi',
                              style: TextStyle(
                                color: Color(0xFF990000),
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),
                        const Text(
                          'SpaceReserve',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 26,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 0.5,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Campus Space Reservation System',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.6),
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 28),

                  // Segmented Role Switcher (Red & Black Aesthetic)
                  Container(
                    padding: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      color: const Color(0xFF161616),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: Colors.white10),
                    ),
                    child: Row(
                      children: [
                        // Student Tab
                        Expanded(
                          child: GestureDetector(
                            onTap: () => setState(() => _selectedRoleIndex = 0),
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 200),
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              decoration: BoxDecoration(
                                color: _selectedRoleIndex == 0
                                    ? const Color(0xFF990000) // IBA Red
                                    : Colors.transparent,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Text(
                                'Student',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  color: _selectedRoleIndex == 0 ? Colors.white : Colors.white60,
                                  fontWeight: FontWeight.w600,
                                  fontSize: 13,
                                ),
                              ),
                            ),
                          ),
                        ),
                        // Faculty / Admin Tab
                        Expanded(
                          child: GestureDetector(
                            onTap: () => setState(() => _selectedRoleIndex = 1),
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 200),
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              decoration: BoxDecoration(
                                color: _selectedRoleIndex == 1
                                    ? const Color(0xFF990000) // IBA Red
                                    : Colors.transparent,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Text(
                                'Faculty / Admin',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  color: _selectedRoleIndex == 1 ? Colors.white : Colors.white60,
                                  fontWeight: FontWeight.w600,
                                  fontSize: 13,
                                ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Main Form Container Card
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: const Color(0xFF141414),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: Colors.white.withOpacity(0.12),
                        width: 1,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.5),
                          blurRadius: 25,
                          offset: const Offset(0, 10),
                        ),
                      ],
                    ),
                    child: _selectedRoleIndex == 0
                        ? const StudentLoginScreen()
                        : const FacultyAdminScreen(),
                  ),
                  const SizedBox(height: 20),

                  // Footer Support Note
                  Text(
                    'Having trouble logging in? Contact Campus IT Support.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.4),
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}