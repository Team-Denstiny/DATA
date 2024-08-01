package com.mysite.demo.MongoDB.Repository;

import com.mysite.demo.MongoDB.DataSchema.DynamicInfoData;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface DynamicInfoRepository extends MongoRepository<DynamicInfoData, String>{
}
