{% load static %}
{% load staff_tags %}
{% get_pending_counts as counts %}
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Pet Portal - Staff Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">

    <style>
        body {
            margin: 0;
            font-family: 'Poppins', sans-serif;
            background-color: var(--bs-body-bg);
            color: var(--bs-body-color);
        }

        .sidebar-link {
            transition: all 0.2s ease-in-out;
        }

        .sidebar-link:hover,
        .sidebar-link.active {
            background-color: #0d6efd !important;
            color: white !important;
            border-radius: 8px;
        }

        .sidebar-link:hover i,
        .sidebar-link.active i {
            color: white !important;
        }
    </style>
</head>

<body>
    <!-- Navbar (Optional for staff, but good for branding) -->
    <nav class="navbar navbar-dark bg-dark shadow-sm">
        <div class="container-fluid px-4">
            <a class="navbar-brand fw-bold" href="{% url 'custom-admin-dashboard' %}">🐾 Staff Portal</a>
            <div class="d-flex align-items-center text-white">
                <span class="me-3">Welcome, {{ user.username }}</span>
            </div>
        </div>
    </nav>

    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar Navigation -->
            <div class="col-md-3 col-lg-2 d-md-block bg-light sidebar shadow-sm p-3 border-end"
                style="min-height: 100vh;">
                <div class="position-sticky pt-3">
                    <h6 class="fw-bold px-3 mb-4 text-muted text-uppercase small">Navigation</h6>
                    <ul class="nav flex-column gap-2 mb-4">
                        <li class="nav-item">
                            <a class="nav-link sidebar-link {% if request.resolver_match.url_name == 'custom-admin-dashboard' %}active{% else %}text-dark{% endif %}"
                                href="{% url 'custom-admin-dashboard' %}">
                                <i class="bi bi-speedometer2 me-2"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link sidebar-link {% if request.resolver_match.url_name == 'admin-request-list' %}active{% else %}text-dark{% endif %} d-flex justify-content-between align-items-center"
                                href="{% url 'admin-request-list' %}">
                                <span><i class="bi bi-file-earmark-text me-2"></i> Pet Reports</span>
                                {% if counts.pet_reports > 0 %}
                                    <span class="badge bg-danger rounded-pill">{{ counts.pet_reports }}</span>
                                {% endif %}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link sidebar-link {% if request.resolver_match.url_name == 'custom-admin-users' %}active{% else %}text-dark{% endif %}"
                                href="{% url 'custom-admin-users' %}">
                                <i class="bi bi-people me-2"></i> Users
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link sidebar-link {% if request.resolver_match.url_name == 'custom-admin-abuse-reports' %}active{% else %}text-dark{% endif %} d-flex justify-content-between align-items-center"
                                href="{% url 'custom-admin-abuse-reports' %}">
                                <span><i class="bi bi-flag me-2"></i> Abuse Reports</span>
                                {% if counts.abuse_reports > 0 %}
                                    <span class="badge bg-danger rounded-pill">{{ counts.abuse_reports }}</span>
                                {% endif %}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link sidebar-link {% if request.resolver_match.url_name == 'admin-contact-requests' %}active{% else %}text-dark{% endif %} d-flex justify-content-between align-items-center"
                                href="{% url 'admin-contact-requests' %}">
                                <span><i class="bi bi-shield-lock me-2"></i> Contact Requests</span>
                                {% if counts.contact_requests > 0 %}
                                    <span class="badge bg-danger rounded-pill">{{ counts.contact_requests }}</span>
                                {% endif %}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link sidebar-link {% if request.resolver_match.url_name == 'admin-admin-requests' %}active{% else %}text-dark{% endif %} d-flex justify-content-between align-items-center"
                                href="{% url 'admin-admin-requests' %}">
                                <span><i class="bi bi-person-lines-fill me-2"></i> Admin Requests</span>
                                {% if counts.admin_requests > 0 %}
                                    <span class="badge bg-danger rounded-pill">{{ counts.admin_requests }}</span>
                                {% endif %}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link sidebar-link {% if request.resolver_match.url_name == 'admin-system-complaints' %}active{% else %}text-dark{% endif %} d-flex justify-content-between align-items-center"
                                href="{% url 'admin-system-complaints' %}">
                                <span><i class="bi bi-exclamation-octagon me-2"></i> System Complaints</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link sidebar-link {% if request.resolver_match.url_name == 'staff-settings' %}active{% else %}text-dark{% endif %}"
                                href="{% url 'staff-settings' %}">
                                <i class="bi bi-gear me-2"></i> Settings
                            </a>
                        </li>
                    </ul>

                    <hr>

                    <ul class="nav flex-column gap-2">
                        <li class="nav-item">
                            <a class="nav-link text-danger fw-bold" href="{% url 'landing' %}">
                                <i class="bi bi-box-arrow-left me-2"></i> Exit Portal
                            </a>
                        </li>
                    </ul>
                </div>
            </div>

            <!-- Main Content Area -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 py-4 bg-light">
                {% block staff_content %}
                {% endblock %}
            </main>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>

</html>