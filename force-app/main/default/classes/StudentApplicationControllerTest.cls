@isTest
private class StudentApplicationControllerTest {

    @testSetup
    static void setupTestData() {
        Contact student = new Contact(
            FirstName = 'Jane',
            LastName = 'Doe',
            Email = 'jane.doe@example.com',
            Phone = '555-0199'
        );
        insert student;

        Lead prospectiveStudent = new Lead(
            FirstName = 'John',
            LastName = 'Smith',
            Email = 'john.smith@example.com',
            Company = 'Prospective Student',
            Status = 'Open - Not Contacted'
        );
        insert prospectiveStudent;
    }

    @isTest
    static void testSubmitScholarshipApplicationSuccess() {
        Map<String, String> applicationData = new Map<String, String>{
            'firstName' => 'John',
            'lastName' => 'Smith',
            'email' => 'john.smith@example.com',
            'phone' => '555-0123',
            'gpa' => '3.8',
            'major' => 'Computer Science',
            'scholarshipType' => 'Merit Scholarship',
            'essay' => 'I am passionate about technology and higher education.'
        };

        Test.startTest();
        String resultId = StudentApplicationController.submitScholarshipApplication(applicationData);
        Test.stopTest();

        System.assertNotEquals(null, resultId, 'Application ID should not be null upon successful submission.');
    }

    @isTest
    static void testSubmitScholarshipApplicationNewStudent() {
        Map<String, String> applicationData = new Map<String, String>{
            'firstName' => 'Alice',
            'lastName' => 'Johnson',
            'email' => 'alice.johnson@example.com',
            'phone' => '555-0177',
            'gpa' => '3.9',
            'major' => 'Biology',
            'scholarshipType' => 'STEM Scholarship',
            'essay' => 'Dedicated to scientific research and innovation.'
        };

        Test.startTest();
        String resultId = StudentApplicationController.submitScholarshipApplication(applicationData);
        Test.stopTest();

        System.assertNotEquals(null, resultId, 'New student application should create a record and return ID.');
    }

    @isTest
    static void testSubmitScholarshipApplicationMissingRequiredFields() {
        Map<String, String> invalidData = new Map<String, String>{
            'firstName' => 'Invalid'
        };

        Boolean exceptionThrown = false;
        Test.startTest();
        try {
            StudentApplicationController.submitScholarshipApplication(invalidData);
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        } catch (Exception e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assert(exceptionThrown, 'An exception should be thrown when required fields are missing.');
    }

    @isTest
    static void testGetApplicationStatus() {
        Contact student = [SELECT Id, Email FROM Contact WHERE Email = 'jane.doe@example.com' LIMIT 1];

        Test.startTest();
        Map<String, Object> statusInfo = StudentApplicationController.getApplicationStatus(student.Email);
        Test.stopTest();

        System.assertNotEquals(null, statusInfo, 'Status info map should not be null.');
    }

    @isTest
    static void testGetScholarshipTypes() {
        Test.startTest();
        List<String> options = StudentApplicationController.getScholarshipTypes();
        Test.stopTest();

        System.assertNotEquals(null, options, 'Scholarship options list should not be null.');
    }
}