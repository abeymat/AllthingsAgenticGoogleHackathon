@IsTest
private class StudentApplicationControllerTest {

    @TestSetup
    static void setupTestData() {
        // Create test Account representing educational institution
        Account testInstitution = new Account(
            Name = 'Universal University'
        );
        insert testInstitution;

        // Create existing applicant Contact record
        Contact existingApplicant = new Contact(
            FirstName = 'Alex',
            LastName = 'Taylor',
            Email = 'alex.taylor@example.com',
            Phone = '5550100100',
            AccountId = testInstitution.Id
        );
        insert existingApplicant;
    }

    @IsTest
    static void testSubmitApplicationSuccess() {
        Account testAcc = [SELECT Id FROM Account WHERE Name = 'Universal University' LIMIT 1];

        Test.startTest();
        Id applicantId = StudentApplicationController.submitApplication(
            'Morgan',
            'Reed',
            'morgan.reed@example.com',
            '5550100200',
            testAcc.Id
        );
        Test.stopTest();

        System.assertNotEquals(null, applicantId, 'The application should return a valid Contact ID upon successful insertion.');
        
        Contact insertedApplicant = [
            SELECT Id, FirstName, LastName, Email, Phone, AccountId 
            FROM Contact 
            WHERE Id = :applicantId 
            LIMIT 1
        ];
        
        System.assertEquals('Morgan', insertedApplicant.FirstName, 'First name should match the submitted value.');
        System.assertEquals('Reed', insertedApplicant.LastName, 'Last name should match the submitted value.');
        System.assertEquals('morgan.reed@example.com', insertedApplicant.Email, 'Email should match the submitted value.');
        System.assertEquals(testAcc.Id, insertedApplicant.AccountId, 'Account ID should link to the specified institution.');
    }

    @IsTest
    static void testSubmitApplicationMissingRequiredField() {
        Account testAcc = [SELECT Id FROM Account WHERE Name = 'Universal University' LIMIT 1];
        Boolean exceptionCaught = false;

        Test.startTest();
        try {
            // Attempt submission with empty last name to trigger validation
            StudentApplicationController.submitApplication(
                'Invalid',
                '',
                'invalid.student@example.com',
                '5550100300',
                testAcc.Id
            );
        } catch (AuraHandledException e) {
            exceptionCaught = true;
        } catch (Exception e) {
            exceptionCaught = true;
        }
        Test.stopTest();

        System.assertEquals(true, exceptionCaught, 'An exception should be caught when submitting invalid/missing required field data.');
    }

    @IsTest
    static void testGetApplicationDetails() {
        Contact existing = [
            SELECT Id, FirstName, LastName, Email 
            FROM Contact 
            WHERE Email = 'alex.taylor@example.com' 
            LIMIT 1
        ];

        Test.startTest();
        Contact result = StudentApplicationController.getApplicationDetails(existing.Id);
        Test.stopTest();

        System.assertNotEquals(null, result, 'Application details should be returned for a valid record ID.');
        System.assertEquals('Alex', result.FirstName, 'First name should match the existing applicant record.');
        System.assertEquals('Taylor', result.LastName, 'Last name should match the existing applicant record.');
    }

    @IsTest
    static void testGetApplicationsByEmail() {
        Test.startTest();
        List<Contact> results = StudentApplicationController.getApplicationsByEmail('alex.taylor@example.com');
        Test.stopTest();

        System.assertNotEquals(null, results, 'Returned list of applications should not be null.');
        System.assertEquals(1, results.size(), 'Exactly one record should match the specified email address.');
        System.assertEquals('Taylor', results[0].LastName, 'The retrieved applicant record should match the test data.');
    }

    @IsTest
    static void testBulkApplicationSubmission() {
        Account testAcc = [SELECT Id FROM Account WHERE Name = 'Universal University' LIMIT 1];
        List<Contact> bulkApplicants = new List<Contact>();

        for (Integer i = 0; i < 200; i++) {
            bulkApplicants.add(new Contact(
                FirstName = 'Student' + i,
                LastName = 'BulkApplicant' + i,
                Email = 'student' + i + '@universaluniversity.edu',
                Phone = '555020' + String.valueOf(i).leftPad(4, '0'),
                AccountId = testAcc.Id
            ));
        }

        Test.startTest();
        List<Id> createdIds = StudentApplicationController.submitBulkApplications(bulkApplicants);
        Test.stopTest();

        System.assertNotEquals(null, createdIds, 'Created ID list should not be null.');
        System.assertEquals(200, createdIds.size(), 'All 200 bulk applicant records should be processed successfully.');

        List<Contact> verifiedRecords = [
            SELECT Id 
            FROM Contact 
            WHERE AccountId = :testAcc.Id AND LastName LIKE 'BulkApplicant%'
        ];
        System.assertEquals(200, verifiedRecords.size(), 'Database should contain exactly 200 newly created bulk applicant records.');
    }
}