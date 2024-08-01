package com.mysite.demo.MongoDB.Repository;

import com.mysite.demo.MongoDB.DataSchema.DentCodeData;

import java.util.Optional;
import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

@Repository
public interface DentCodeRepository extends MongoRepository<DentCodeData, String>{
    @Query("{'kor': {'$regex': ?0}}")
    public List<DentCodeData> findByKor(String name);
}
