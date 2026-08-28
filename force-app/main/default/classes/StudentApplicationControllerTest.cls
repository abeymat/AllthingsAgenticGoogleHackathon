@IsTest
private class StudentApplicationControllerTest {

    @TestSetup
    static void setupTestData() {
        Account testAccount = new Account(
            Name = 'Test University'
        );
        insert testAccount;

        Contact testStudent = new Contact(
            FirstName = 'Jane',
            LastName = 'Doe',
            Email = 'jane.doe@example.com',
            Phone = '555-0199',
            AccountId = testAccount.Id
        );
        insert testStudent;

        Opportunity testTuitionFee = new Opportunity(
            Name = 'Jane Doe - Fall 2025 Tuition',
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30),
            Amount = 5000.00,
            AccountId = testAccount.Id
        );
        insert testTuitionFee;
    }

    @IsTest
    static void testGetStudentApplicationsSuccess() {
        Contact student = [SELECT Id, LastName, Email FROM Contact WHERE LastName = 'Doe' LIMIT 1];

        Test.startTest();
        List<Contact> students = StudentApplicationController.getStudentApplications();
        Test.stopTest();

        System.assertNotEquals(null, students, 'Student applications list should not be null.');
        System.assert(students.size() > 0, 'Expected at least one student application record.');
    }

    @IsTest
    static void testGetStudentDetailsById() {
        Contact student = [SELECT Id, FirstName, LastName, Email FROM Contact WHERE LastName = 'Doe' LIMIT 1];

        Test.startTest();
        Contact result = StudentApplicationController.getStudentDetails(student.Id);
        Test.stopTest();

        System.assertNotEquals(null, result, 'Student detail should be returned.');
        System.assertEquals('Jane', result.FirstName, 'First name should match.');
    }

    @IsTest
    static void testSubmitApplication() {
        Test.startTest();
        Contact newStudent = new Contact(
            FirstName = 'John',
            LastName = 'Smith',
            Email = 'john.smith@example.com'
        );
        Id studentId = StudentApplicationController.submitApplication(newStudent, 'Fall 2025', 4500.00);
        Test.stopTest();

        System.assertNotEquals(null, studentId, 'Inserted student application ID should not be null.');
        Contact insertedContact = [SELECT Id, LastName FROM Contact WHERE Id = :studentId];
        System.assertEquals('Smith', insertedContact.LastName, 'LastName should be Smith.');
    }

    @IsTest
    static void testProcessTuitionPayment() {
        Opportunity opp = [SELECT Id, StageName, Amount FROM Opportunity LIMIT 1];

        Test.startTest();
        Boolean paymentSuccess = StudentApplicationController.processTuitionPayment(opp.Id, 5000.00, 'Credit Card');
        Test.stopTest();

        System.assertEquals(true, paymentSuccess, 'Payment processing should return true for valid input.');
        Opportunity updatedOpp = [SELECT Id, StageName FROM Opportunity WHERE Id = :opp.Id];
        System.assertEquals('Closed Won', updatedOpp.StageName, 'Opportunity stage should be updated to Closed Won.');
    }

    @IsTest
    static void testProcessTuitionPaymentInvalidAmount() {
        Opportunity opp = [SELECT Id FROM Opportunity LIMIT 1];

        Test.startTest();
        try {
            StudentApplicationController.processTuitionPayment(opp.Id, -100.00, 'Credit Card');
            System.assert(false, 'Expected Exception for negative payment amount.');
        } catch (Exception ex) {
            System.assertNotEquals(null, ex, 'Exception should be caught for invalid payment amount.');
        }
        Test.stopTest();
    }

    @IsTest
    static void testGetStudentDetailsInvalidId() {
        Test.startTest();
        try {
            Contact result = StudentApplicationController.getStudentDetails(null);
        } catch (Exception ex) {
            System.assertNotEquals(null, ex.getMessage(), 'Exception message should not be empty.');
        }
        Test.stopTest();
    }
}