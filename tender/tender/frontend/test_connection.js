// Test frontend-backend connection
async function testConnection() {
    console.log('🧪 Testing Frontend-Backend Connection...');
    
    try {
        // Test health endpoint
        const healthResponse = await fetch('http://localhost:8000/health');
        const healthData = await healthResponse.json();
        console.log('✅ Backend Health:', healthData);
        
        // Test tender search
        const searchResponse = await fetch('http://localhost:8000/tenders/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ keywords: 'construction' })
        });
        const searchData = await searchResponse.json();
        console.log('✅ Tender Search:', searchData.count, 'tenders found');
        
        // Test public API
        const publicResponse = await fetch('http://localhost:8000/api/enriched-releases');
        const publicData = await publicResponse.json();
        console.log('✅ Public API:', publicData.length, 'items');
        
        console.log('🎉 All frontend-backend tests passed!');
        return true;
    } catch (error) {
        console.error('❌ Connection test failed:', error);
        return false;
    }
}

// Run the test
testConnection();