<!doctype html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <title> MyApp by MyDomain</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta content="$1.00 per minute Caption Platform" name="description" />
    <meta content="MyDomain" name="author" />
    <meta name="csrf-token" content="{{ csrf_token }}" />
    <!-- App favicon -->
    <link rel="shortcut icon" href="https://storage.googleapis.com/cirrus-static-assets/frontend_assets/favicon.ico">
    
    {% include 'frontend_theme/headlayout.html' %}
</head>

<body data-layout="vertical" data-topbar="light">
<!-- Begin page -->
<div class="container-fluid">
    <div id="layout-wrapper">
        @include('layouts.hor-menu')
        <!-- ============================================================== -->
        <!-- Start right Content here -->
        <!-- ============================================================== -->
        <div class="main-content">
            <div class="page-content">
                {% block content %}
                {% endblock %}
            </div>
            {% include 'frontend_theme/footer.html'}
        </div>
        <!-- ============================================================== -->
        <!-- End Right content here -->
        <!-- ============================================================== -->
    </div>
    <!-- END wrapper -->
</div>
<!-- Right Sidebar -->
<!-- @include('layouts.right-sidebar') -->
<!-- END Right Sidebar -->

{% include 'frontend_theme/footer-scripts.html'}

</body>

</html>