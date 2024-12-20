<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blockchain Marketplace</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
</head>
<body class="bg-gradient-to-br from-gray-50 to-gray-100">
    <div class="min-h-screen">
        <!-- Navigation -->
        <nav class="bg-white shadow-lg">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex items-center">
                        <a href="/" class="flex items-center">
                            <i class="fas fa-link text-blue-600 text-2xl mr-2"></i>
                            <span class="text-xl font-bold text-gray-800">Blockchain Marketplace</span>
                        </a>
                    </div>
                    {% if show_database %}
                    <div class="flex items-center">
                        <a href="/" class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors">
                            <i class="fas fa-home mr-2"></i>Back to Home
                        </a>
                    </div>
                    {% endif %}
                </div>
            </div>
        </nav>

        {% if not show_database %}
        <!-- Main Content -->
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <!-- Hero Section -->
            <div class="text-center mb-12">
                <h1 class="text-4xl font-bold text-gray-900 mb-4">Welcome to Blockchain Marketplace</h1>
                <p class="text-lg text-gray-600">A secure and decentralized platform for buying and selling products</p>
            </div>

            <!-- Action Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
                <!-- Buy Card -->
                <a href="/buy" class="transform transition-all duration-300 hover:scale-105 hover:-rotate-1">
                    <div class="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl relative overflow-hidden group">
                        <div class="absolute inset-0 bg-gradient-to-r from-green-500/10 to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        <div class="relative">
                            <div class="flex items-center mb-6">
                                <div class="bg-green-100 p-3 rounded-lg">
                                    <i class="fas fa-shopping-cart text-green-500 text-2xl"></i>
                                </div>
                                <h2 class="text-2xl font-semibold text-gray-800 ml-4">Buy Products</h2>
                            </div>
                            <p class="text-gray-600">Browse available products and make secure purchases using blockchain technology</p>
                        </div>
                    </div>
                </a>

                <!-- Sell Card -->
                <a href="/sell" class="transform transition-all duration-300 hover:scale-105 hover:rotate-1">
                    <div class="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl relative overflow-hidden group">
                        <div class="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        <div class="relative">
                            <div class="flex items-center mb-6">
                                <div class="bg-purple-100 p-3 rounded-lg">
                                    <i class="fas fa-store text-purple-500 text-2xl"></i>
                                </div>
                                <h2 class="text-2xl font-semibold text-gray-800 ml-4">Sell Products</h2>
                            </div>
                            <p class="text-gray-600">List your products for sale on our decentralized marketplace</p>
                        </div>
                    </div>
                </a>
            </div>

            <!-- Feature Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                <div class="bg-white rounded-xl shadow-md p-6">
                    <div class="flex items-center justify-center mb-4">
                        <div class="bg-blue-100 p-3 rounded-full">
                            <i class="fas fa-shield-alt text-blue-500 text-xl"></i>
                        </div>
                    </div>
                    <h3 class="text-lg font-semibold text-center text-gray-800 mb-2">Secure Transactions</h3>
                    <p class="text-gray-600 text-center">All transactions are secured by blockchain technology</p>
                </div>

                <div class="bg-white rounded-xl shadow-md p-6">
                    <div class="flex items-center justify-center mb-4">
                        <div class="bg-green-100 p-3 rounded-full">
                            <i class="fas fa-sync text-green-500 text-xl"></i>
                        </div>
                    </div>
                    <h3 class="text-lg font-semibold text-center text-gray-800 mb-2">Real-time Updates</h3>
                    <p class="text-gray-600 text-center">See product listings and updates in real-time</p>
                </div>

                <div class="bg-white rounded-xl shadow-md p-6">
                    <div class="flex items-center justify-center mb-4">
                        <div class="bg-purple-100 p-3 rounded-full">
                            <i class="fas fa-network-wired text-purple-500 text-xl"></i>
                        </div>
                    </div>
                    <h3 class="text-lg font-semibold text-center text-gray-800 mb-2">Decentralized</h3>
                    <p class="text-gray-600 text-center">No central authority, fully peer-to-peer</p>
                </div>
            </div>

            <!-- Transaction Explorer Button -->
            <div class="text-center">
                <button onclick="window.location.href='/view_database'"
                        class="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-8 py-3 rounded-full
                               hover:from-blue-600 hover:to-purple-600 transition-all duration-300 transform hover:scale-105
                               shadow-lg hover:shadow-xl">
                    <i class="fas fa-database mr-2"></i>
                    View Transaction History
                </button>
            </div>
        </div>
        {% else %}
        <!-- Database View Content (kept from previous version) -->
        <!-- ... Your existing database view content ... -->
        {% endif %}
    </div>
</body>
</html>